"""SavedPlace model — a frequently used location."""

from ..extensions import db
from ..utils.time import iso, utcnow


class SavedPlace(db.Model):
    """A labelled location the user can pick quickly in the Journey Planner."""

    __tablename__ = "saved_places"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    label = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "created_at": iso(self.created_at),
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<SavedPlace {self.id} {self.label}>"
