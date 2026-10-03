"""AI explanation endpoint. OpenAI explains; the engine decides."""

from flask import Blueprint, request

from ..extensions import db
from ..models import Journey
from ..services import ai_service
from ..utils.auth import current_user_id, login_required
from ..utils.responses import error_response, success_response

bp = Blueprint("ai", __name__, url_prefix="/ai")


def _payload() -> dict:
    return request.get_json(silent=True) or {}


@bp.post("/explain-route")
@login_required
def explain_route():
    """Explain a recommendation from already-computed routes or a stored journey."""
    data = _payload()
    preference = data.get("preference") or "balanced"
    ranked = data.get("routes")
    source = data.get("source") or ""
    destination = data.get("destination") or ""

    if not ranked and data.get("journey_id"):
        journey = db.session.get(Journey, int(data["journey_id"]))
        if journey is None or journey.user_id != current_user_id():
            return error_response("NOT_FOUND", "Journey not found", 404)
        source = source or journey.source_label
        destination = destination or journey.dest_label
        preference = data.get("preference") or journey.preference
        ranked = [route.to_dict() for route in journey.routes]

    if not ranked:
        return error_response(
            "VALIDATION_ERROR", "provide routes or a journey_id to explain", 400
        )

    if data.get("route_id"):
        ranked = sorted(
            ranked,
            key=lambda route: 0 if route.get("id") == data["route_id"] else 1,
        )

    result = ai_service.explain_recommendation(source, destination, preference, ranked)
    return success_response(result, 200)
