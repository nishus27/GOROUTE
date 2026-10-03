"""Booking endpoints."""

from flask import Blueprint, request

from ..extensions import db
from ..models import Booking, Notification
from ..utils.auth import current_user_id, login_required
from ..utils.responses import error_response, success_response

bp = Blueprint("bookings", __name__, url_prefix="/bookings")


def _payload() -> dict:
    return request.get_json(silent=True) or {}


@bp.get("")
@login_required
def list_bookings():
    """Return the user's bookings, newest first."""
    bookings = (
        Booking.query.filter_by(user_id=current_user_id())
        .order_by(Booking.created_at.desc())
        .limit(50)
        .all()
    )
    return success_response({"bookings": [item.to_dict() for item in bookings]}, 200)


@bp.post("")
@login_required
def create_booking():
    """Create a booking for a bookable leg of a chosen route."""
    data = _payload()
    provider = (data.get("provider") or "").strip()
    if not provider:
        return error_response("VALIDATION_ERROR", "provider is required", 400)

    booking = Booking(
        user_id=current_user_id(),
        route_id=data.get("route_id"),
        provider=provider,
        status="pending",
        fare=float(data.get("fare") or 0.0),
        scheduled_at=data.get("scheduled_at"),
    )
    booking.set_details(data.get("details") or {})
    db.session.add(booking)

    db.session.add(
        Notification(
            user_id=current_user_id(),
            type="booking_update",
            title="Booking created",
            message=f"Your {provider} booking is pending confirmation.",
        )
    )
    db.session.commit()
    return success_response({"booking": booking.to_dict()}, 201)


@bp.post("/<int:booking_id>/cancel")
@login_required
def cancel_booking(booking_id: int):
    """Cancel a booking."""
    booking = db.session.get(Booking, booking_id)
    if booking is None or booking.user_id != current_user_id():
        return error_response("NOT_FOUND", "Booking not found", 404)

    booking.status = "cancelled"
    db.session.add(
        Notification(
            user_id=current_user_id(),
            type="booking_update",
            title="Booking cancelled",
            message=f"Your {booking.provider} booking was cancelled.",
        )
    )
    db.session.commit()
    return success_response({"booking": booking.to_dict()}, 200)
