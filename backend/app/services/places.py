"""Place resolution and geo helpers used by the route provider.

A small built-in gazetteer of well-known locations lets the backend produce
plausible distances without an external geocoder. Unknown places fall back to a
deterministic distance derived from the place names, so results are stable.
"""

import hashlib
import math

# Approximate coordinates for common locations (lat, lng).
GAZETTEER: dict[str, tuple[float, float]] = {
    "thane": (19.2183, 72.9781),
    "thane west": (19.1976, 72.9639),
    "andheri": (19.1197, 72.8464),
    "andheri east": (19.1136, 72.8697),
    "andheri west": (19.1364, 72.8296),
    "bandra": (19.0596, 72.8295),
    "kurla": (19.0726, 72.8845),
    "dadar": (19.0178, 72.8478),
    "ghatkopar": (19.0863, 72.9081),
    "powai": (19.1176, 72.9060),
    "mulund": (19.1726, 72.9425),
    "bhandup": (19.1440, 72.9372),
    "borivali": (19.2307, 72.8567),
    "kandivali": (19.2094, 72.8526),
    "malad": (19.1860, 72.8484),
    "chembur": (19.0522, 72.9005),
    "vashi": (19.0771, 72.9986),
    "navi mumbai": (19.0330, 73.0297),
    "cst": (18.9398, 72.8355),
    "csmt": (18.9398, 72.8355),
    "churchgate": (18.9322, 72.8264),
    "mumbai central": (18.9696, 72.8194),
    "lower parel": (18.9962, 72.8258),
    "worli": (19.0176, 72.8119),
    "mumbai airport": (19.0896, 72.8656),
    "airport": (19.0896, 72.8656),
    "panvel": (18.9894, 73.1175),
    "kalyan": (19.2437, 73.1355),
    "dombivli": (19.2184, 73.0869),
    "sion": (19.0434, 72.8619),
    "wadala": (19.0176, 72.8628),
    "jogeshwari": (19.1364, 72.8481),
    "goregaon": (19.1663, 72.8526),
    "mira road": (19.2813, 72.8681),
    "vasai": (19.3919, 72.8397),
}

_EARTH_RADIUS_KM = 6371.0088
_ROAD_FACTOR = 1.28  # straight-line distance → approximate road distance


def _normalize(name: str) -> str:
    return " ".join((name or "").strip().lower().replace(",", " ").split())


def resolve_place(name: str) -> tuple[float, float] | None:
    """Return (lat, lng) for a known place name, else None."""
    key = _normalize(name)
    if not key:
        return None
    if key in GAZETTEER:
        return GAZETTEER[key]
    # Try a substring match (e.g. "Thane Station" -> "thane").
    for candidate, coords in GAZETTEER.items():
        if candidate in key or key in candidate:
            return coords
    return None


def _deterministic_distance_km(source: str, destination: str) -> float:
    """Stable pseudo-distance for unknown places, in a plausible urban range."""
    digest = hashlib.sha256(f"{_normalize(source)}|{_normalize(destination)}".encode())
    bucket = int(digest.hexdigest()[:8], 16) % 1900  # 0..1899
    return round(11.0 + bucket / 100.0, 1)  # 11.0 .. 29.9 km


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lng1 = math.radians(a[0]), math.radians(a[1])
    lat2, lng2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(h))


def distance_km(source: str, destination: str) -> float:
    """Approximate road distance between two place names, in kilometres."""
    a = resolve_place(source)
    b = resolve_place(destination)
    if a and b:
        return round(_haversine_km(a, b) * _ROAD_FACTOR, 1)
    return _deterministic_distance_km(source, destination)


def coordinates(name: str) -> tuple[float | None, float | None]:
    """Return (lat, lng) for a place name, or (None, None) if unknown."""
    coords = resolve_place(name)
    return coords if coords else (None, None)
