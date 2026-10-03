"""DailyCommute model — a recurring commute planned automatically."""

from ..extensions import db
from ..utils.time import iso, utcnow


class DailyCommute(db.Model):
    """A saved recurring commute the user wants re-evaluated day after day."""

    __tablename__ = "daily_commutes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    source_label = db.Column(db.String(255), nullable=False)
    source_lat = db.Column(db.Float)
    source_lng = db.Column(db.Float)
    dest_label = db.Column(db.String(255), nullable=False)
    dest_lat = db.Column(db.Float)
    dest_lng = db.Column(db.Float)
    departure_time = db.Column(db.String(64))
    days_of_week = db.Column(db.String(64), default="Mon,Tue,Wed,Thu,Fri")
    preference = db.Column(db.String(32), nullable=False, default="balanced")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source_label,
            "destination": self.dest_label,
            "departure_time": self.departure_time,
            "days_of_week": self.days_of_week,
            "preference": self.preference,
            "is_active": bool(self.is_active),
            "created_at": iso(self.created_at),
            "updated_at": iso(self.updated_at),
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<DailyCommute {self.id} {self.source_label}->{self.dest_label}>"
