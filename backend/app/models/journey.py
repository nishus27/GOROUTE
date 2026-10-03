"""Journey model — a single journey request (a search) made by a user."""

from ..extensions import db
from ..utils.time import iso, utcnow


class Journey(db.Model):
    """A journey search with its source, destination and chosen preference."""

    __tablename__ = "journeys"

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
    preference = db.Column(db.String(32), nullable=False, default="balanced")
    status = db.Column(db.String(32), nullable=False, default="planned")
    selected_route_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    routes = db.relationship(
        "Route",
        back_populates="journey",
        cascade="all, delete-orphan",
        order_by="Route.score.desc()",
    )

    def to_dict(self, include_routes: bool = False) -> dict:
        data = {
            "id": self.id,
            "source": self.source_label,
            "destination": self.dest_label,
            "departure_time": self.departure_time,
            "preference": self.preference,
            "status": self.status,
            "selected_route_id": self.selected_route_id,
            "created_at": iso(self.created_at),
        }
        if include_routes:
            data["routes"] = [route.to_dict() for route in self.routes]
        return data

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Journey {self.id} {self.source_label}->{self.dest_label}>"
