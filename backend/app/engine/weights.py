"""Scoring weights and preference presets.

These weights are FIXED by the GoRoute product specification. Do not change them.
They must always sum to 1.0.
"""

# The six scoring factors.
FACTORS = ("time", "reliability", "cost", "waiting", "transfers", "walking")

# Default ("balanced") weights — the product specification.
# Travel Time 30% · Reliability 20% · Cost 15% · Waiting 10% · Transfers 10% · Walking 15%
DEFAULT_WEIGHTS = {
    "time": 0.30,
    "reliability": 0.20,
    "cost": 0.15,
    "waiting": 0.10,
    "transfers": 0.10,
    "walking": 0.15,
}

# Named preference presets. Each emphasises one factor; every set sums to 1.0.
PREFERENCE_PRESETS = {
    "balanced": DEFAULT_WEIGHTS,
    "fastest": {
        "time": 0.50,
        "reliability": 0.15,
        "cost": 0.10,
        "waiting": 0.10,
        "transfers": 0.05,
        "walking": 0.10,
    },
    "cheapest": {
        "time": 0.20,
        "reliability": 0.10,
        "cost": 0.40,
        "waiting": 0.10,
        "transfers": 0.10,
        "walking": 0.10,
    },
    "most_reliable": {
        "time": 0.15,
        "reliability": 0.45,
        "cost": 0.10,
        "waiting": 0.10,
        "transfers": 0.10,
        "walking": 0.10,
    },
    "least_walking": {
        "time": 0.20,
        "reliability": 0.15,
        "cost": 0.10,
        "waiting": 0.05,
        "transfers": 0.10,
        "walking": 0.40,
    },
}

VALID_PREFERENCES = tuple(PREFERENCE_PRESETS.keys())


def normalize_weights(weights: dict) -> dict:
    """Return ``weights`` renormalized so the six factors sum to 1.0."""
    clean = {factor: float(weights.get(factor, 0.0) or 0.0) for factor in FACTORS}
    total = sum(clean.values())
    if total <= 0:
        return dict(DEFAULT_WEIGHTS)
    return {factor: clean[factor] / total for factor in FACTORS}


def resolve_weights(preference: str | None = None, weights: dict | None = None) -> dict:
    """Resolve the weight set for a request.

    Explicit ``weights`` win; otherwise the named ``preference`` preset is used;
    otherwise the default (balanced) weights apply.
    """
    if weights:
        return normalize_weights(weights)
    if preference and preference in PREFERENCE_PRESETS:
        return normalize_weights(PREFERENCE_PRESETS[preference])
    return dict(DEFAULT_WEIGHTS)
