"""Journey planning service.

Orchestrates the core flow: load candidate routes (Google Maps when configured,
otherwise the backend route provider), run the deterministic Decision Engine,
ask for an explanation, persist the Journey, and return the ranked result.
"""

import logging

from ..engine import score_routes
from ..extensions import db
from ..integrations import GoogleMapsClient
from ..models import Journey, Route
from . import ai_service
from .places import coordinates, distance_km
from .route_provider import build_candidates

logger = logging.getLogger(__name__)

_google = GoogleMapsClient()


def load_candidates(
    source: str,
    destination: str,
    departure_time: str | None = None,
    modes: list[str] | None = None,
) -> tuple[list[dict], str]:
    """Return ``(candidates, route_source)``.

    Google Maps is preferred when a key is configured; the backend route
    provider keeps the application fully functional otherwise.
    """
    candidates = _google.fetch_candidates(source, destination, departure_time, modes)
    if candidates:
        return candidates, "google_maps"
    return build_candidates(source, destination, departure_time, modes), "goroute"


def plan_journey(
    user_id: int,
    source: str,
    destination: str,
    preference: str = "balanced",
    departure_time: str | None = None,
    modes: list[str] | None = None,
    persist: bool = True,
) -> dict:
    """Run the full journey-planning flow and return the ranked routes."""
    candidates, route_source = load_candidates(source, destination, departure_time, modes)
    result = score_routes(candidates, preference)
    ranked = result["ranked"]
    explanation = ai_service.explain_recommendation(source, destination, preference, ranked)

    journey_id = None
    if persist and ranked:
        journey_id = _persist(user_id, source, destination, preference, departure_time, ranked)

    return {
        "journey_id": journey_id,
        "source": source,
        "destination": destination,
        "departure_time": departure_time,
        "preference": preference,
        "distance_km": distance_km(source, destination),
        "weights": result["weights"],
        "routes": ranked,
        "recommended_route_id": result["recommended_route_id"],
        "explanation": explanation["explanation"],
        "explanation_source": explanation["source"],
        "route_source": route_source,
    }


def _persist(user_id, source, destination, preference, departure_time, ranked) -> int:
    src_lat, src_lng = coordinates(source)
    dst_lat, dst_lng = coordinates(destination)

    journey = Journey(
        user_id=user_id,
        source_label=source,
        source_lat=src_lat,
        source_lng=src_lng,
        dest_label=destination,
        dest_lat=dst_lat,
        dest_lng=dst_lng,
        departure_time=departure_time,
        preference=preference,
        status="planned",
    )
    db.session.add(journey)
    db.session.flush()

    for route in ranked:
        metrics = route["metrics"]
        row = Route(
            journey_id=journey.id,
            mode_summary=route["mode_summary"],
            total_duration_min=metrics["total_duration_min"],
            total_cost=metrics["total_cost"],
            waiting_time_min=metrics["waiting_time_min"],
            transfers=metrics["transfers"],
            walking_distance_m=metrics["walking_distance_m"],
            reliability=metrics["reliability"],
            score=route["score"],
            is_selected=bool(route.get("is_selected")),
        )
        row.set_legs(route.get("legs", []))
        db.session.add(row)

    db.session.commit()
    return journey.id
