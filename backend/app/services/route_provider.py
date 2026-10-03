"""Backend route provider.

Produces the candidate multimodal routes that the Decision Engine evaluates.
It covers every transport mode GoRoute supports — Local Train, Metro, Bus, Cab,
Auto, Walking — and the required multimodal combinations (Train+Auto,
Train+Walk, Metro+Walk, Bus+Auto, Bus+Walk).

The provider is deterministic: the same source/destination always yields the
same candidate metrics, so scores and rankings are reproducible.

When a Google Maps key is configured, :mod:`app.integrations.google_maps`
supplies real route data and takes precedence (see ``JourneyService``); this
provider keeps the application fully functional without external keys.
"""

import hashlib

from .places import coordinates, distance_km

# Per-mode characteristics: cruise speed, fare model, reliability, typical
# waiting time and typical access/egress walking distance.
MODE_PROFILES: dict[str, dict] = {
    "train": {"speed": 42, "base": 5, "per_km": 1.0, "reliability": 0.82, "wait": 6, "walk_m": 900},
    "metro": {"speed": 34, "base": 6, "per_km": 1.4, "reliability": 0.90, "wait": 4, "walk_m": 800},
    "bus": {"speed": 17, "base": 8, "per_km": 1.1, "reliability": 0.62, "wait": 8, "walk_m": 400},
    "cab": {"speed": 25, "base": 45, "per_km": 15.0, "reliability": 0.74, "wait": 4, "walk_m": 100},
    "auto": {"speed": 23, "base": 28, "per_km": 12.0, "reliability": 0.70, "wait": 3, "walk_m": 150},
    "walking": {"speed": 4.8, "base": 0, "per_km": 0.0, "reliability": 1.0, "wait": 0, "walk_m": 0},
}

MODE_LABELS = {
    "train": "Local Train",
    "metro": "Metro",
    "bus": "Bus",
    "cab": "Cab",
    "auto": "Auto",
    "walking": "Walking",
}

# Each spec: a stable code, a display summary, its legs (mode, distance share)
# and an optional maximum distance beyond which the option is impractical.
ROUTE_SPECS: list[dict] = [
    {"code": "train", "summary": "Local Train", "legs": [("train", 1.0)], "max_km": None},
    {"code": "metro", "summary": "Metro", "legs": [("metro", 1.0)], "max_km": None},
    {"code": "bus", "summary": "Bus", "legs": [("bus", 1.0)], "max_km": None},
    {"code": "cab", "summary": "Cab", "legs": [("cab", 1.0)], "max_km": None},
    {"code": "auto", "summary": "Auto", "legs": [("auto", 1.0)], "max_km": None},
    # Walking is offered as a standalone option for walkable distances only.
    {"code": "walking", "summary": "Walking", "legs": [("walking", 1.0)], "max_km": 4.0},
    {"code": "train+auto", "summary": "Train \u2192 Auto", "legs": [("train", 0.75), ("auto", 0.25)], "max_km": None},
    {"code": "train+walk", "summary": "Train \u2192 Walk", "legs": [("train", 0.85), ("walking", 0.15)], "max_km": None},
    {"code": "metro+walk", "summary": "Metro \u2192 Walk", "legs": [("metro", 0.80), ("walking", 0.20)], "max_km": None},
    {"code": "bus+auto", "summary": "Bus \u2192 Auto", "legs": [("bus", 0.70), ("auto", 0.30)], "max_km": None},
    {"code": "bus+walk", "summary": "Bus \u2192 Walk", "legs": [("bus", 0.80), ("walking", 0.20)], "max_km": None},
]

TRANSFER_OVERHEAD_MIN = 3


def _seed(source: str, destination: str, code: str) -> int:
    key = f"{source.strip().lower()}|{destination.strip().lower()}|{code}"
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)


def _jitter(seed: int, salt: int, span: int) -> int:
    """Deterministic integer in ``[-span, span]`` derived from the seed."""
    if span <= 0:
        return 0
    return ((seed >> (salt * 3 + 1)) % (2 * span + 1)) - span


def _leg_metrics(mode: str, distance: float) -> dict:
    profile = MODE_PROFILES[mode]
    duration = distance / profile["speed"] * 60
    cost = profile["base"] + profile["per_km"] * distance
    if mode == "walking":
        walking_m = int(round(distance * 1000))
    else:
        walking_m = int(profile["walk_m"])
    return {
        "duration_min": duration,
        "cost": cost,
        "wait_min": profile["wait"],
        "walking_m": walking_m,
        "reliability": profile["reliability"],
    }



def _instruction(mode: str, origin: str) -> str:
    if mode == "walking":
        return f"Walk from {origin}"
    if mode in ("cab", "auto"):
        return f"Take a {MODE_LABELS[mode]} from {origin}"
    return f"Board the {MODE_LABELS[mode]} at {origin}"


def _reliability(parts: list[tuple[str, float]]) -> float:
    if len(parts) == 1:
        return MODE_PROFILES[parts[0][0]]["reliability"]
    trunk = MODE_PROFILES[parts[0][0]]["reliability"]
    feeder = MODE_PROFILES[parts[-1][0]]["reliability"]
    return round(trunk * 0.6 + feeder * 0.4, 2)


def _build_legs(source: str, destination: str, spec: dict, total_km: float) -> list[dict]:
    parts = spec["legs"]
    multi = len(parts) > 1
    legs: list[dict] = []
    for index, (mode, share) in enumerate(parts):
        leg_km = round(total_km * share, 1)
        metrics = _leg_metrics(mode, leg_km)
        if multi:
            origin = source if index == 0 else "Interchange"
            target = "Interchange" if index == 0 else destination
        else:
            origin, target = source, destination
        lat, lng = coordinates(origin)
        legs.append(
            {
                "mode": mode,
                "mode_label": MODE_LABELS[mode],
                "from": origin,
                "to": target,
                "duration_min": int(round(metrics["duration_min"])),
                "distance_km": leg_km,
                "cost": round(metrics["cost"], 1),
                "instruction": _instruction(mode, origin),
                "latitude": lat,
                "longitude": lng,
            }
        )
    return legs


def build_candidates(
    source: str,
    destination: str,
    departure_time: str | None = None,
    modes: list[str] | None = None,
) -> list[dict]:
    """Return the candidate routes for a source/destination pair.

    ``modes`` optionally restricts the returned modes (e.g. ``["train", "metro"]``).
    """
    total_km = distance_km(source, destination)
    allowed = {m.strip().lower() for m in modes} if modes else None

    candidates: list[dict] = []
    for spec in ROUTE_SPECS:
        spec_modes = [mode for mode, _ in spec["legs"]]
        if allowed and not set(spec_modes) & allowed:
            continue
        max_km = spec.get("max_km")
        if max_km is not None and total_km > max_km:
            continue

        seed = _seed(source, destination, spec["code"])
        legs = _build_legs(source, destination, spec, total_km)

        duration = sum(leg["duration_min"] for leg in legs)
        if len(legs) > 1:
            duration += TRANSFER_OVERHEAD_MIN
        duration = max(1, int(round(duration + _jitter(seed, 0, 2))))

        cost = sum(leg["cost"] for leg in legs)
        cost = round(cost * (1 + _jitter(seed, 1, 4) / 100.0), 1)

        waiting = 0
        walking_m = 0
        for (mode, _share), leg in zip(spec["legs"], legs):
            leg_metrics = _leg_metrics(mode, leg["distance_km"])
            waiting += leg_metrics["wait_min"]
            walking_m += leg_metrics["walking_m"]
        waiting = max(0, int(round(waiting)) + _jitter(seed, 2, 1))
        walking_m = int(round(walking_m / 10.0) * 10)

        candidates.append(
            {
                "id": spec["code"],
                "mode_summary": spec["summary"],
                "modes": spec_modes,
                "legs": legs,
                "metrics": {
                    "total_duration_min": duration,
                    "total_cost": cost,
                    "waiting_time_min": waiting,
                    "transfers": max(0, len(legs) - 1),
                    "walking_distance_m": walking_m,
                    "reliability": _reliability(spec["legs"]),
                },
            }
        )

    return candidates


def apply_incident(candidates: list[dict], incident: dict) -> list[dict]:
    """Apply a traffic/delay incident to the affected route and return new copies.

    Every candidate is returned, so the caller can re-score and re-rank the full
    set — not just the affected route.
    """
    incident = incident or {}
    target = incident.get("route_id")
    incident_type = (incident.get("type") or "traffic").lower()
    delay = int(incident.get("delay_minutes") or 0)

    updated: list[dict] = []
    for candidate in candidates:
        item = {
            "id": candidate["id"],
            "mode_summary": candidate["mode_summary"],
            "modes": list(candidate["modes"]),
            "legs": [dict(leg) for leg in candidate["legs"]],
            "metrics": dict(candidate["metrics"]),
        }
        if target and item["id"] == target and delay:
            metrics = item["metrics"]
            metrics["total_duration_min"] += delay
            if incident_type == "traffic":
                metrics["reliability"] = round(max(0.0, metrics["reliability"] * 0.92), 2)
                metrics["waiting_time_min"] += max(1, delay // 5)
            else:  # generic delay
                metrics["waiting_time_min"] += max(1, round(delay * 0.3))
                metrics["reliability"] = round(max(0.0, metrics["reliability"] * 0.97), 2)
            item["incident_applied"] = {
                "type": incident_type,
                "delay_minutes": delay,
                "route_id": item["id"],
            }
        updated.append(item)
    return updated
