"""GoRoute backend application factory."""

import os

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from .config import INSTANCE_DIR, Config
from .extensions import cors, db


def create_app(config_object=Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        instance_path=str(INSTANCE_DIR),
        instance_relative_config=True,
    )
    app.config.from_object(config_object)

    # Ensure the SQLite location exists before the DB is created.
    os.makedirs(app.instance_path, exist_ok=True)

    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)

    # Create the SQLite database and tables automatically if missing.
    with app.app_context():
        from . import models  # noqa: F401  (register models before create_all)

        db.create_all()

    return app


def _init_extensions(app: Flask) -> None:
    db.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )


def _register_blueprints(app: Flask) -> None:
    from .routes import register_blueprints

    register_blueprints(app)


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        code = (err.name or "HTTP_ERROR").upper().replace(" ", "_")
        return jsonify({"error": {"code": code, "message": err.description}}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err: Exception):
        app.logger.exception("Unhandled error: %s", err)
        return (
            jsonify(
                {
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                    }
                }
            ),
            500,
        )
