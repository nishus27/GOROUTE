"""Journey route endpoints: search, score and reroute."""

from flask import Blueprint, request

from ..engine import score_routes
from ..services import plan_journey
from ..services import reroute as reroute_service
from ..utils.auth import current_user_id, login_required
from ..utils.responses import error_response, success_response
from ..utils.validation import validate_reroute_request, validate_route_request

bp = Blueprint("routes", __name__, url_prefix="/routes")


def _payload() -> dict:
    return request.get_json(silent=True) or {}


@bp.post("/search")
@login_required
def search():
    """Plan a journey: return scored, ranked multimodal routes + recommendation."""
    data = _payload()
    errors = validate_route_request(data)
    if errors:
        return error_response("VALIDATION_ERROR", errors[0], 400)

    result = plan_journey(
        user_id=current_user_id(),
        source=data["source"].strip(),
        destination=data["destination"].strip(),
        preference=(data.get("preference") or "balanced"),
        departure_time=data.get("departure_time"),
        modes=data.get("modes"),
    )
    return success_response(result, 200)


@bp.post("/score")
@login_required
def score():
    """Pure Decision Engine call: normalize, weight, score and rank."""
    data = _payload()
    routes = data.get("routes")
    if not isinstance(routes, list) or not routes:
        return error_response("VALIDATION_ERROR", "routes must be a non-empty list", 400)

    result = score_routes(
        routes,
        preference=data.get("preference") or "balanced",
        weights=data.get("weights"),
    )
    return success_response(result, 200)


@bp.post("/reroute")
@login_required
def reroute():
    """Re-evaluate every candidate route after an incident and re-rank them."""
    data = _payload()
    errors = validate_reroute_request(data)
    if errors:
        return error_response("VALIDATION_ERROR", errors[0], 400)

    result = reroute_service(
        user_id=current_user_id(),
        source=data["source"].strip(),
        destination=data["destination"].strip(),
        preference=(data.get("preference") or "balanced"),
        incident=data.get("incident") or {},
        previous_recommended_route_id=(
            data.get("previous_recommended_route_id") or data.get("previous_route_id")
        ),
        departure_time=data.get("departure_time"),
    )
    return success_response(result, 200)
