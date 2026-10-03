"""Daily Commute endpoints."""

from flask import Blueprint, request

from ..engine.weights import VALID_PREFERENCES
from ..extensions import db
from ..models import DailyCommute
from ..utils.auth import current_user_id, login_required
from ..utils.responses import error_response, success_response

bp = Blueprint("daily_commute", __name__, url_prefix="/daily-commute")


def _payload() -> dict:
    return request.get_json(silent=True) or {}


def _active(user_id: int) -> DailyCommute | None:
    return (
        DailyCommute.query.filter_by(user_id=user_id)
        .order_by(DailyCommute.updated_at.desc())
        .first()
    )


def _validate(data: dict) -> list[str]:
    errors: list[str] = []
    if not (data.get("source") or "").strip():
        errors.append("source is required")
    if not (data.get("destination") or "").strip():
        errors.append("destination is required")
    preference = data.get("preference")
    if preference and preference not in VALID_PREFERENCES:
        errors.append(f"preference must be one of {', '.join(VALID_PREFERENCES)}")
    return errors


def _apply(commute: DailyCommute, data: dict) -> None:
    commute.source_label = data["source"].strip()
    commute.dest_label = data["destination"].strip()
    commute.departure_time = data.get("departure_time")
    commute.days_of_week = data.get("days_of_week") or commute.days_of_week
    commute.preference = data.get("preference") or commute.preference
    commute.is_active = bool(data.get("is_active", True))


@bp.get("")
@login_required
def get_commute():
    """Return the user's configured daily commute (or null)."""
    commute = _active(current_user_id())
    return success_response(
        {"daily_commute": commute.to_dict() if commute else None}, 200
    )


@bp.post("")
@login_required
def create_commute():
    """Create a recurring commute."""
    data = _payload()
    errors = _validate(data)
    if errors:
        return error_response("VALIDATION_ERROR", errors[0], 400)

    commute = DailyCommute(
        user_id=current_user_id(),
        source_label=data["source"].strip(),
        dest_label=data["destination"].strip(),
        departure_time=data.get("departure_time"),
        days_of_week=data.get("days_of_week") or "Mon,Tue,Wed,Thu,Fri",
        preference=data.get("preference") or "balanced",
        is_active=bool(data.get("is_active", True)),
    )
    db.session.add(commute)
    db.session.commit()
    return success_response({"daily_commute": commute.to_dict()}, 201)


@bp.put("")
@login_required
def update_commute():
    """Update the user's daily commute."""
    commute = _active(current_user_id())
    if commute is None:
        return create_commute()

    data = _payload()
    errors = _validate(data)
    if errors:
        return error_response("VALIDATION_ERROR", errors[0], 400)

    _apply(commute, data)
    db.session.commit()
    return success_response({"daily_commute": commute.to_dict()}, 200)
