"""Health check endpoint."""

from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    """Simple liveness probe used by the frontend and tests."""
    return jsonify({"status": "ok", "service": "goroute"})
