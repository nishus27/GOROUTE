"""Route model — a candidate route produced for a Journey, including its score."""

import json

from ..extensions import db
from ..utils.time import iso, utcnow


class Route(db.Model):
    """A scored candidate route belonging to a Journey."""

    __tablename__ = "routes"

    id = db.Column(db.Integer, primary_key=True)
    journey_id = db.Column(
        db.Integer, db.ForeignKey("journeys.id"), nullable=False, index=True
    )
    mode_summary = db.Column(db.String(120), nullable=False)
    legs_json = db.Column(db.Text, nullable=False, default="[]")
    total_duration_min = db.Column(db.Integer, nullable=False, default=0)
    total_cost = db.Column(db.Float, nullable=False, default=0.0)
    waiting_time_min = db.Column(db.Integer, nullable=False, default=0)
    transfers = db.Column(db.Integer, nullable=False, default=0)
    walking_distance_m = db.Column(db.Integer, nullable=False, default=0)
    reliability = db.Column(db.Float, nullable=False, default=0.0)
    score = db.Column(db.Float, nullable=False, default=0.0)
    is_selected = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    journey = db.relationship("Journey", back_populates="routes")

    def set_legs(self, legs: list[dict]) -> None:
        self.legs_json = json.dumps(legs or [])

    def get_legs(self) -> list[dict]:
        try:
            return json.loads(self.legs_json or "[]")
        except (ValueError, TypeError):  # pragma: no cover - defensive
            return []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "mode_summary": self.mode_summary,
            "score": self.score,
            "is_selected": bool(self.is_selected),
            "metrics": {
                "total_duration_min": self.total_duration_min,
                "total_cost": self.total_cost,
                "waiting_time_min": self.waiting_time_min,
                "transfers": self.transfers,
                "walking_distance_m": self.walking_distance_m,
                "reliability": self.reliability,
            },
            "legs": self.get_legs(),
            "created_at": iso(self.created_at),
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Route {self.id} {self.mode_summary} score={self.score}>"
