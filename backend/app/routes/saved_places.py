"""Saved Places endpoints."""

from flask import Blueprint, request

from ..extensions import db
from ..models import SavedPlace
from ..utils.auth import current_user_id, login_required
from ..utils.responses import error_response, success_response

bp = Blueprint("saved_places", __name__, url_prefix="/saved-places")


def _payload() -> dict:
    return request.get_json(silent=True) or {}


def _validate(data: dict) -> list[str]:
    errors: list[str] = []
    if not (data.get("label") or "").strip():
        errors.append("label is required")
    if not (data.get("address") or "").strip():
        errors.append("address is required")
    return errors


@bp.get("")
@login_required
def list_places():
    """List the current user's saved places."""
    places = (
        SavedPlace.query.filter_by(user_id=current_user_id())
        .order_by(SavedPlace.created_at.desc())
        .all()
    )
    return success_response({"saved_places": [place.to_dict() for place in places]}, 200)


@bp.post("")
@login_required
def create_place():
    """Create a saved place."""
    data = _payload()
    errors = _validate(data)
    if errors:
        return error_response("VALIDATION_ERROR", errors[0], 400)

    place = SavedPlace(
        user_id=current_user_id(),
        label=data["label"].strip(),
        address=data["address"].strip(),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
    )
    db.session.add(place)
    db.session.commit()
    return success_response({"saved_place": place.to_dict()}, 201)


@bp.put("/<int:place_id>")
@login_required
def update_place(place_id: int):
    """Update a saved place."""
    place = db.session.get(SavedPlace, place_id)
    if place is None or place.user_id != current_user_id():
        return error_response("NOT_FOUND", "Saved place not found", 404)

    data = _payload()
    errors = _validate(data)
    if errors:
        return error_response("VALIDATION_ERROR", errors[0], 400)

    place.label = data["label"].strip()
    place.address = data["address"].strip()
    if "latitude" in data:
        place.latitude = data.get("latitude")
    if "longitude" in data:
        place.longitude = data.get("longitude")
    db.session.commit()
    return success_response({"saved_place": place.to_dict()}, 200)


@bp.delete("/<int:place_id>")
@login_required
def delete_place(place_id: int):
    """Delete a saved place."""
    place = db.session.get(SavedPlace, place_id)
    if place is None or place.user_id != current_user_id():
        return error_response("NOT_FOUND", "Saved place not found", 404)

    db.session.delete(place)
    db.session.commit()
    return success_response({"success": True}, 200)
