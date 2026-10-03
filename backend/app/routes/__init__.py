"""API blueprint registration.

All endpoints are mounted under the ``/api`` prefix.
"""

from flask import Blueprint

from .ai import bp as ai_bp
from .auth import bp as auth_bp
from .bookings import bp as bookings_bp
from .daily_commute import bp as daily_commute_bp
from .health import bp as health_bp
from .insights import bp as insights_bp
from .journeys import bp as journeys_bp
from .notifications import bp as notifications_bp
from .routes import bp as routes_bp
from .saved_places import bp as saved_places_bp

api_bp = Blueprint("api", __name__, url_prefix="/api")
api_bp.register_blueprint(health_bp)
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(routes_bp)
api_bp.register_blueprint(ai_bp)
api_bp.register_blueprint(journeys_bp)
api_bp.register_blueprint(saved_places_bp)
api_bp.register_blueprint(daily_commute_bp)
api_bp.register_blueprint(notifications_bp)
api_bp.register_blueprint(bookings_bp)
api_bp.register_blueprint(insights_bp)


def register_blueprints(app) -> None:
    """Attach all API blueprints to the Flask application."""
    app.register_blueprint(api_bp)
