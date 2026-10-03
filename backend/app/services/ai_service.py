"""AI explanation service.

The Decision Engine decides; OpenAI explains. If OpenAI is not configured (or
unreachable) a deterministic explanation is generated from the engine's own
output, so the recommendation is always explained.
"""

from ..integrations import OpenAIExplainer
from ..engine.weights import resolve_weights

_explainer = OpenAIExplainer()

PREFERENCE_LABELS = {
    "balanced": "balanced",
    "fastest": "fastest",
    "cheapest": "cheapest",
    "most_reliable": "most reliable",
    "least_walking": "least walking",
}

FACTOR_LABELS = {
    "time": "travel time",
    "reliability": "reliability",
    "cost": "cost",
    "waiting": "waiting time",
    "transfers": "transfers",
    "walking": "walking distance",
}


def explain_recommendation(
    source: str,
    destination: str,
    preference: str,
    ranked: list[dict],
    change: dict | None = None,
) -> dict:
    """Return ``{"explanation": str, "source": "openai"|"engine"}``."""
    if not ranked:
        return {"explanation": "", "source": "engine"}

    winner = ranked[0]
    context = _build_context(source, destination, preference, ranked, change)
    text = _explainer.explain(context)
    if text:
        return {"explanation": text, "source": "openai"}
    return {"explanation": _deterministic_explanation(context), "source": "engine"}


def _build_context(source, destination, preference, ranked, change) -> dict:
    winner = ranked[0]
    return {
        "source": source,
        "destination": destination,
        "preference": preference,
        "recommended": {
            "mode": winner.get("mode_summary"),
            "score": winner.get("score"),
            "metrics": winner.get("metrics"),
        },
        "compared_routes": [
            {
                "mode": route.get("mode_summary"),
                "score": route.get("score"),
                "metrics": route.get("metrics"),
            }
            for route in ranked
        ],
        "change": change,
    }


def _top_factors(winner: dict, preference: str) -> list[str]:
    weights = resolve_weights(preference)
    normalized = winner.get("normalized") or {}
    contributions = {
        factor: weights.get(factor, 0.0) * normalized.get(factor, 0.0)
        for factor in weights
    }
    ranked = sorted(contributions.items(), key=lambda item: item[1], reverse=True)
    return [FACTOR_LABELS[factor] for factor, value in ranked[:2] if value > 0]


def _deterministic_explanation(context: dict) -> str:
    winner = context["recommended"]
    metrics = winner["metrics"]
    preference = context["preference"]
    label = PREFERENCE_LABELS.get(preference, preference)
    ranked = context["compared_routes"]

    parts = [
        f"{winner['mode']} is recommended for your {label} preference, "
        f"scoring {winner['score']}/100."
    ]
    detail = (
        f"It takes about {metrics['total_duration_min']} min at "
        f"\u20b9{metrics['total_cost']:.0f}, with "
        f"{metrics['transfers']} transfer(s), "
        f"{metrics['waiting_time_min']} min waiting and "
        f"{metrics['walking_distance_m']} m walking."
    )
    parts.append(detail)

    runner_up = next((r for r in ranked[1:] if r["mode"] != winner["mode"]), None)
    if runner_up:
        parts.append(
            f"The next best option, {runner_up['mode']}, scores "
            f"{runner_up['score']}/100."
        )

    change = context.get("change")
    if change and change.get("changed"):
        parts.append(
            f"Conditions changed: {change.get('reason')} "
            f"All routes were re-scored and the recommendation was updated."
        )
    return " ".join(parts)
