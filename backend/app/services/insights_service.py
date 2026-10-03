"""Weekly insights service — aggregates the user's last 7 days of journeys."""

from datetime import timedelta

from ..models import Journey, Notification
from ..utils.time import utcnow


def weekly_insights(user_id: int) -> dict:
    """Return aggregated commuting metrics for the past seven days."""
    since = utcnow() - timedelta(days=7)
    journeys = (
        Journey.query.filter(Journey.user_id == user_id, Journey.created_at >= since)
        .order_by(Journey.created_at.desc())
        .all()
    )

    total_time = 0
    total_cost = 0.0
    total_transfers = 0
    mode_counts: dict[str, int] = {}

    for journey in journeys:
        selected = next((route for route in journey.routes if route.is_selected), None)
        if selected is None:
            continue
        total_time += selected.total_duration_min
        total_cost += selected.total_cost
        total_transfers += selected.transfers
        for leg in selected.get_legs():
            mode = leg.get("mode_label") or leg.get("mode")
            if mode:
                mode_counts[mode] = mode_counts.get(mode, 0) + 1

    route_changes = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.type == "route_change",
        Notification.created_at >= since,
    ).count()

    return {
        "period_days": 7,
        "total_journeys": len(journeys),
        "total_time_min": total_time,
        "total_cost": round(total_cost, 1),
        "total_transfers": total_transfers,
        "route_changes": route_changes,
        "mode_breakdown": [
            {"mode": mode, "count": count}
            for mode, count in sorted(mode_counts.items(), key=lambda item: -item[1])
        ],
    }
