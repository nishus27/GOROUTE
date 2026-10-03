"""Request payload validation for authentication and journey endpoints."""

import re

from ..engine.weights import VALID_PREFERENCES

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 6



def validate_signup(payload: dict) -> list[str]:
    """Return a list of validation error messages (empty if valid)."""
    errors: list[str] = []
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""

    if not name:
        errors.append("name is required")
    if not email:
        errors.append("email is required")
    elif not EMAIL_RE.match(email):
        errors.append("email is not valid")
    if not password:
        errors.append("password is required")
    elif len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"password must be at least {MIN_PASSWORD_LENGTH} characters")

    return errors


def validate_login(payload: dict) -> list[str]:
    """Return a list of validation error messages (empty if valid)."""
    errors: list[str] = []
    if not (payload.get("email") or "").strip():
        errors.append("email is required")
    if not payload.get("password"):
        errors.append("password is required")
    return errors


def validate_route_request(payload: dict) -> list[str]:
    """Validate a journey search / score request."""
    errors: list[str] = []
    if not (payload.get("source") or "").strip():
        errors.append("source is required")
    if not (payload.get("destination") or "").strip():
        errors.append("destination is required")
    preference = payload.get("preference")
    if preference and preference not in VALID_PREFERENCES:
        errors.append(f"preference must be one of {', '.join(VALID_PREFERENCES)}")
    return errors


def validate_reroute_request(payload: dict) -> list[str]:
    """Validate a reroute request."""
    errors = validate_route_request(payload)
    incident = payload.get("incident")
    if incident is not None and not isinstance(incident, dict):
        errors.append("incident must be an object")
    elif isinstance(incident, dict) and incident.get("delay_minutes") is not None:
        try:
            int(incident["delay_minutes"])
        except (TypeError, ValueError):
            errors.append("incident.delay_minutes must be a number")
    return errors
