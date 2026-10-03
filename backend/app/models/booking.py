"""Booking model — a reservation for a bookable leg of a chosen route."""

import json

from ..extensions import db
from ..utils.time import iso, utcnow


class Booking(db.Model):
    """A booking (cab/auto/transit) linked to a user and optionally a route."""

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"))
    provider = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="pending")
    fare = db.Column(db.Float, nullable=False, default=0.0)
    scheduled_at = db.Column(db.String(64))
    details_json = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    def set_details(self, details: dict) -> None:
        self.details_json = json.dumps(details or {})

    def get_details(self) -> dict:
        try:
            return json.loads(self.details_json or "{}")
        except (ValueError, TypeError):  # pragma: no cover - defensive
            return {}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "route_id": self.route_id,
            "provider": self.provider,
            "status": self.status,
            "fare": self.fare,
            "scheduled_at": self.scheduled_at,
            "details": self.get_details(),
            "created_at": iso(self.created_at),
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Booking {self.id} {self.provider} {self.status}>"
