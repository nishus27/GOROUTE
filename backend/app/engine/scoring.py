"""The deterministic route scoring engine.

Turns candidate routes into a ranked list with a 0–100 score each and selects
the best route for the requested preference. Pure, deterministic code — no
randomness, no clock dependence, no AI in the score path.
"""

from .normalize import metric_value, normalize_factor
from .weights import FACTORS, resolve_weights


def _rank_key(route: dict) -> tuple:
    """Stable tie-break: score desc, then duration, cost, transfers, id."""
    metrics = route["metrics"]
    return (
        -float(route["score"]),
        float(metrics["total_duration_min"]),
        float(metrics["total_cost"]),
        float(metrics["transfers"]),
        str(route.get("id", "")),
    )


def score_routes(
    candidates: list[dict],
    preference: str | None = "balanced",
    weights: dict | None = None,
) -> dict:
    """Score, rank and select the best route from ``candidates``.

    Returns ``{"ranked": [...], "recommended_route_id": <id>, "weights": {...}}``.
    Each ranked route gains ``score`` (0–100), ``normalized`` (per factor) and
    ``is_selected`` (True for the winner).
    """
    resolved = resolve_weights(preference, weights)

    if not candidates:
        return {"ranked": [], "recommended_route_id": None, "weights": resolved}

    # 1. Collect raw values per factor for min–max normalization.
    values = {factor: [metric_value(r, factor) for r in candidates] for factor in FACTORS}

    # 2. Normalize + apply weights to compute a 0–100 score.
    scored: list[dict] = []
    for route in candidates:
        normalized = {
            factor: normalize_factor(factor, metric_value(route, factor), values[factor])
            for factor in FACTORS
        }
        raw = sum(resolved[factor] * normalized[factor] for factor in FACTORS)
        item = dict(route)
        item["normalized"] = {factor: round(normalized[factor], 4) for factor in FACTORS}
        item["score"] = round(raw * 100, 1)
        scored.append(item)

    # 3. Rank descending by score with a stable tie-break.
    ranked = sorted(scored, key=_rank_key)

    # 4. Mark the winner and record the rank position.
    for index, route in enumerate(ranked):
        route["rank"] = index + 1
        route["is_selected"] = index == 0

    return {
        "ranked": ranked,
        "recommended_route_id": ranked[0].get("id"),
        "weights": resolved,
    }
