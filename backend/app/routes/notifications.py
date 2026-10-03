"""Notification endpoints."""

from flask import Blueprint

from ..extensions import db
from ..models import Notification
from ..utils.auth import current_user_id, login_required
from ..utils.responses import error_response, success_response

bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@bp.get("")
@login_required
def list_notifications():
    """Return the user's notifications and the unread count."""
    notifications = (
        Notification.query.filter_by(user_id=current_user_id())
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    unread = sum(1 for item in notifications if not item.is_read)
    return success_response(
        {
            "notifications": [item.to_dict() for item in notifications],
            "unread_count": unread,
        },
        200,
    )


@bp.post("/<int:notification_id>/read")
@login_required
def mark_read(notification_id: int):
    """Mark a single notification as read."""
    item = db.session.get(Notification, notification_id)
    if item is None or item.user_id != current_user_id():
        return error_response("NOT_FOUND", "Notification not found", 404)

    item.is_read = True
    db.session.commit()
    return success_response({"notification": item.to_dict()}, 200)


@bp.post("/read-all")
@login_required
def mark_all_read():
    """Mark every notification as read."""
    Notification.query.filter_by(user_id=current_user_id(), is_read=False).update(
        {"is_read": True}
    )
    db.session.commit()
    return success_response({"success": True}, 200)
