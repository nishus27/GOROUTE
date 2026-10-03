"""Standard JSON response helpers.

Success responses return the payload as-is.
Error responses always use the shape:

    { "error": { "code": "SOME_CODE", "message": "human readable" } }
"""

from flask import jsonify


def success_response(data: dict | None = None, status: int = 200):
    """Return a JSON success response."""
    return jsonify(data if data is not None else {}), status


def error_response(code: str, message: str, status: int = 400):
    """Return a JSON error response in the standard GoRoute shape."""
    return jsonify({"error": {"code": code, "message": message}}), status
