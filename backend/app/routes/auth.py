"""Authentication endpoints (session-based)."""

from flask import Blueprint, request

from ..extensions import db
from ..models import User
from ..utils.auth import current_user_id, login_required, login_user, logout_user
from ..utils.responses import error_response, success_response
from ..utils.validation import validate_login, validate_signup

bp = Blueprint("auth", __name__, url_prefix="/auth")


def _payload() -> dict:
    return request.get_json(silent=True) or {}


@bp.post("/signup")
def signup():
    """Create a new account and start a session."""
    data = _payload()

    errors = validate_signup(data)
    if errors:
        return error_response("VALIDATION_ERROR", errors[0], 400)

    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first() is not None:
        return error_response(
            "EMAIL_IN_USE", "An account with this email already exists", 409
        )

    user = User(name=data["name"].strip(), email=email)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    login_user(user.id)
    return success_response({"user": user.to_dict()}, 201)


@bp.post("/login")
def login():
    """Verify credentials and start a session."""
    data = _payload()

    errors = validate_login(data)
    if errors:
        return error_response("VALIDATION_ERROR", errors[0], 400)

    email = data["email"].strip().lower()
    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(data["password"]):
        return error_response(
            "INVALID_CREDENTIALS", "Invalid email or password", 401
        )

    login_user(user.id)
    return success_response({"user": user.to_dict()}, 200)


@bp.post("/logout")
def logout():
    """End the current session (idempotent)."""
    logout_user()
    return success_response({"success": True}, 200)


@bp.get("/me")
@login_required
def me():
    """Return the currently authenticated user."""
    user = db.session.get(User, current_user_id())
    if user is None:
        logout_user()
        return error_response("UNAUTHORIZED", "Authentication required", 401)
    return success_response({"user": user.to_dict()}, 200)
