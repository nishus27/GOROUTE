"""Session-based authentication helpers."""

from functools import wraps

from flask import session

from .responses import error_response

SESSION_USER_KEY = "user_id"


def current_user_id() -> int | None:
    """Return the logged-in user's id from the session, or None."""
    return session.get(SESSION_USER_KEY)


def login_user(user_id: int) -> None:
    """Start a fresh authenticated session for the given user."""
    session.clear()
    session[SESSION_USER_KEY] = user_id
    session.permanent = True


def logout_user() -> None:
    """Clear the current session."""
    session.clear()


def login_required(view):
    """Decorator: reject unauthenticated requests with a 401 JSON error."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user_id() is None:
            return error_response("UNAUTHORIZED", "Authentication required", 401)
        return view(*args, **kwargs)

    return wrapped
