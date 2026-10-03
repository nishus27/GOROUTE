"""Journey history endpoints."""

from flask import Blueprint

from ..extensions import db
from ..models import Journey
from ..utils.auth import current_user_id, login_required
from ..utils.responses import error_response, success_response

bp = Blueprint("journeys", __name__, url_prefix="/journeys")


@bp.get("")
@login_required
def list_journeys():
    """Return the current user's journeys, newest first, with compared routes."""
    journeys = (
        Journey.query.filter_by(user_id=current_user_id())
        .order_by(Journey.created_at.desc())
        .limit(50)
        .all()
    )
    return success_response(
        {"journeys": [journey.to_dict(include_routes=True) for journey in journeys]}, 200
    )


@bp.get("/<int:journey_id>")
@login_required
def get_journey(journey_id: int):
    """Return one journey with all compared routes and their scores."""
    journey = db.session.get(Journey, journey_id)
    if journey is None or journey.user_id != current_user_id():
        return error_response("NOT_FOUND", "Journey not found", 404)
    return success_response({"journey": journey.to_dict(include_routes=True)}, 200)
