"""Notification model — an event message shown to the user."""

from ..extensions import db
from ..utils.time import iso, utcnow


class Notification(db.Model):
    """A route-change / reminder / booking-update message for a user."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    type = db.Column(db.String(32), nullable=False, default="route_change")
    title = db.Column(db.String(160), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "is_read": bool(self.is_read),
            "created_at": iso(self.created_at),
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Notification {self.id} {self.type}>"
