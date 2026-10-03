"""Time helpers (UTC)."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def iso(value: datetime | None) -> str | None:
    """Serialize a datetime to ISO-8601, or None."""
    return value.isoformat() if value else None
