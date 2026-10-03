"""Dynamic rerouting service.

Rerouting reuses the same Decision Engine — it does not score differently. When
conditions change, every candidate route is re-evaluated: affected metrics are
updated, all routes are re-scored, the full set is re-ranked, and the new
recommendation is compared with the previous one.
"""

from ..engine import score_routes
from ..extensions import db
from ..models import Notification
from . import ai_service
from .journey_service import load_candidates
from .route_provider import apply_incident


def reroute(
    user_id: int,
    source: str,
    destination: str,
    preference: str = "balanced",
    incident: dict | None = None,
    previous_recommended_route_id: str | None = None,
    departure_time: str | None = None,
    notify: bool = True,
) -> dict:
    """Re-evaluate all candidate routes after an incident and re-rank them."""
    incident = incident or {}

    # 1. Baseline candidates (identical inputs -> identical baseline).
    base_candidates, route_source = load_candidates(source, destination, departure_time)
    base_result = score_routes(base_candidates, preference)
    previous_id = previous_recommended_route_id or base_result["recommended_route_id"]

    # 2. Apply the incident to the affected route, then re-score EVERY route.
    updated_candidates = apply_incident(base_candidates, incident)
    result = score_routes(updated_candidates, preference)
    ranked = result["ranked"]
    new_id = result["recommended_route_id"]

    changed = new_id != previous_id
    change_reason = _change_reason(changed, previous_id, new_id, ranked, incident)

    explanation = ai_service.explain_recommendation(
        source,
        destination,
        preference,
        ranked,
        change={"changed": changed, "reason": change_reason},
    )

    if changed and notify:
        _notify(user_id, source, destination, previous_id, new_id, change_reason)

    return {
        "source": source,
        "destination": destination,
        "preference": preference,
        "weights": result["weights"],
        "routes": ranked,
        "recommended_route_id": new_id,
        "previous_recommended_route_id": previous_id,
        "changed": changed,
        "change_reason": change_reason,
        "incident": incident,
        "affected_route_id": incident.get("route_id"),
        "explanation": explanation["explanation"],
        "explanation_source": explanation["source"],
        "route_source": route_source,
    }


def _route_by_id(ranked: list[dict], route_id: str | None) -> dict | None:
    return next((route for route in ranked if route.get("id") == route_id), None)


def _change_reason(changed, previous_id, new_id, ranked, incident) -> str:
    incident_type = (incident.get("type") or "traffic").lower()
    delay = incident.get("delay_minutes")
    affected = incident.get("route_id")
    affected_route = _route_by_id(ranked, affected)
    affected_label = affected_route["mode_summary"] if affected_route else affected
    winner = _route_by_id(ranked, new_id)
    winner_label = winner["mode_summary"] if winner else new_id

    if affected_label and delay:
        lead = f"{incident_type.capitalize()} added {delay} min to {affected_label}."
    else:
        lead = f"{incident_type.capitalize()} conditions were applied."

    if changed:
        return f"{lead} {winner_label} now leads after re-scoring every route."
    return f"{lead} {winner_label} remains the best route after re-scoring every route."


def _notify(user_id, source, destination, previous_id, new_id, reason) -> None:
    notification = Notification(
        user_id=user_id,
        type="route_change",
        title="Recommendation updated",
        message=f"{source} \u2192 {destination}: {reason}",
    )
    db.session.add(notification)
    db.session.commit()
