"""Weekly Insights endpoint."""

from flask import Blueprint

from ..services import weekly_insights
from ..utils.auth import current_user_id, login_required
from ..utils.responses import success_response

bp = Blueprint("insights", __name__)


@bp.get("/weekly-insights")
@login_required
def get_weekly_insights():
    """Return aggregated metrics for the user's past seven days."""
    return success_response(weekly_insights(current_user_id()), 200)
