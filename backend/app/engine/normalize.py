"""Metric extraction and min–max normalization.

Each metric becomes a 0–1 "goodness" value where 1 is best.
"""

# Factors where a lower raw value is better.
LOWER_IS_BETTER = ("time", "cost", "waiting", "transfers", "walking")
# Factors where a higher raw value is better.
HIGHER_IS_BETTER = ("reliability",)


def metric_value(route: dict, factor: str) -> float:
    """Read the raw metric for ``factor`` from a candidate route."""
    metrics = route.get("metrics", route)
    if factor == "time":
        return float(metrics["total_duration_min"])
    if factor == "reliability":
        return float(metrics["reliability"])
    if factor == "cost":
        return float(metrics["total_cost"])
    if factor == "waiting":
        return float(metrics["waiting_time_min"])
    if factor == "transfers":
        return float(metrics["transfers"])
    if factor == "walking":
        return float(metrics["walking_distance_m"])
    raise KeyError(f"unknown factor: {factor}")


def normalize_factor(factor: str, value: float, values: list[float]) -> float:
    """Min–max normalize ``value`` against the candidate set.

    Degenerate case (max == min): the factor cannot discriminate, so every route
    scores 1.0 and is not penalized.
    """
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return 1.0
    if factor in LOWER_IS_BETTER:
        return (hi - value) / (hi - lo)
    return (value - lo) / (hi - lo)
