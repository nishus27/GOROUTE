"""Google Maps integration.

Google Maps *provides route data*; it never makes the decision. When
``GOOGLE_MAPS_API_KEY`` is configured this client fetches real routes from the
Google Directions API and normalizes them into the candidate shape the Decision
Engine consumes. When it is not configured — or the API is unreachable — the
caller falls back to the backend route provider, so GoRoute stays functional.
"""

import json
import logging
import os
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"

# Google vehicle types -> GoRoute modes.
VEHICLE_TO_MODE = {
    "HEAVY_RAIL": "train",
    "COMMUTER_TRAIN": "train",
    "RAIL": "train",
    "SUBWAY": "metro",
    "METRO_RAIL": "metro",
    "TRAM": "metro",
    "BUS": "bus",
    "INTERCITY_BUS": "bus",
    "TROLLEYBUS": "bus",
}

MODE_LABELS = {
    "train": "Local Train",
    "metro": "Metro",
    "bus": "Bus",
    "cab": "Cab",
    "auto": "Auto",
    "walking": "Walking",
}


class GoogleMapsClient:
    """Thin, dependency-free client for the Google Directions API."""

    def __init__(self, api_key: str | None = None, timeout: int = 6) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY") or ""
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        """True when a Google Maps API key is available."""
        return bool(self.api_key)

    def fetch_candidates(
        self,
        source: str,
        destination: str,
        departure_time: str | None = None,
        modes: list[str] | None = None,
    ) -> list[dict] | None:
        """Return candidates from Google Maps, or None to use the fallback provider."""
        if not self.is_configured:
            return None

        candidates: list[dict] = []
        try:
            for travel_mode in ("transit", "driving"):
                candidates.extend(
                    self._fetch_travel_mode(source, destination, travel_mode, departure_time)
                )
        except Exception as exc:  # pragma: no cover - network dependent
            logger.warning("Google Maps request failed, using backend provider: %s", exc)
            return None

        return candidates or None

    def _fetch_travel_mode(
        self,
        source: str,
        destination: str,
        travel_mode: str,
        departure_time: str | None,
    ) -> list[dict]:
        params = {
            "origin": source,
            "destination": destination,
            "mode": travel_mode,
            "alternatives": "true",
            "key": self.api_key,
        }
        if travel_mode == "driving":
            params["departure_time"] = "now"
        elif departure_time:
            params["departure_time"] = departure_time

        url = f"{DIRECTIONS_URL}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))

        if payload.get("status") not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(payload.get("status", "UNKNOWN"))

        return [
            self._to_candidate(route, travel_mode, index)
            for index, route in enumerate(payload.get("routes", []))
        ]

    def _to_candidate(self, route: dict, travel_mode: str, index: int) -> dict:
        legs = route.get("legs", [])
        duration_s = sum(leg.get("duration", {}).get("value", 0) for leg in legs)
        traffic_s = sum(
            leg.get("duration_in_traffic", {}).get("value", 0) for leg in legs
        ) or duration_s

        modes: list[str] = []
        google_legs: list[dict] = []
        transfers = 0
        waiting_min = 0
        walking_m = 0

        for leg in legs:
            for step in leg.get("steps", []):
                step_mode = self._step_mode(step, travel_mode)
                if step_mode not in modes:
                    modes.append(step_mode)
                step_duration = int(round(step.get("duration", {}).get("value", 0) / 60))
                step_distance = step.get("distance", {}).get("value", 0)
                if step_mode == "walking":
                    walking_m += step_distance
                elif google_legs:
                    transfers += 1
                start = step.get("start_location", {}) or {}
                transit_details = step.get("transit_details") or {}
                google_legs.append(
                    {
                        "mode": step_mode,
                        "mode_label": MODE_LABELS[step_mode],
                        "from": (transit_details.get("departure_stop") or {}).get("name")
                        or start.get("lat"),
                        "to": (transit_details.get("arrival_stop") or {}).get("name")
                        or step.get("end_location", {}).get("lat"),
                        "duration_min": step_duration,
                        "distance_km": round(step_distance / 1000.0, 1),
                        "cost": 0.0,
                        "instruction": self._strip_html(step.get("html_instructions", "")),
                        "latitude": start.get("lat"),
                        "longitude": start.get("lng"),
                    }
                )
                transit = step.get("transit_details")
                if transit:
                    waiting_min += self._transit_wait_minutes(transit)

        primary = modes[0] if modes else ("cab" if travel_mode == "driving" else "bus")
        return {
            "id": f"gmaps-{travel_mode}-{index}",
            "mode_summary": " \u2192 ".join(MODE_LABELS.get(m, m) for m in modes)
            or MODE_LABELS.get(primary, "Route"),
            "modes": modes or [primary],
            "legs": google_legs,
            "metrics": {
                "total_duration_min": int(round(duration_s / 60)),
                "total_cost": 0.0,
                "waiting_time_min": waiting_min,
                "transfers": transfers,
                "walking_distance_m": walking_m,
                "reliability": self._reliability(duration_s, traffic_s),
            },
            "provider": "google_maps",
        }

    @staticmethod
    def _step_mode(step: dict, travel_mode: str) -> str:
        transit = step.get("transit_details")
        if transit:
            vehicle = (transit.get("line", {}).get("vehicle", {}) or {}).get("type", "")
            return VEHICLE_TO_MODE.get(vehicle, "bus")
        if step.get("travel_mode") == "WALKING":
            return "walking"
        return "cab" if travel_mode == "driving" else "walking"

    @staticmethod
    def _transit_wait_minutes(transit: dict) -> int:
        departure = transit.get("departure_time", {}).get("value")
        arrival = transit.get("arrival_time", {}).get("value")
        if departure and arrival and arrival > departure:
            return max(0, int(round((arrival - departure) / 60)))
        return 0

    @staticmethod
    def _reliability(duration_s: int, traffic_s: int) -> float:
        if duration_s <= 0:
            return 0.8
        ratio = traffic_s / duration_s
        return round(min(0.99, max(0.3, 1.0 - (ratio - 1.0) * 0.5)), 2)

    @staticmethod
    def _strip_html(text: str) -> str:
        result = []
        inside = False
        for char in text or "":
            if char == "<":
                inside = True
            elif char == ">":
                inside = False
            elif not inside:
                result.append(char)
        return "".join(result).strip()
