"""User account model."""

from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(db.Model):
    """An authenticated GoRoute account.

    Passwords are only ever stored as a secure hash (never plain text).
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        """Hash and store the given plain-text password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Return True if the plain-text password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """Public representation of the user (never includes the password)."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<User {self.id} {self.email}>"
