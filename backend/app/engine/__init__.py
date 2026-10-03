"""The deterministic Route Decision Engine.

Public API:
    from app.engine import score_routes, DEFAULT_WEIGHTS, PREFERENCE_PRESETS
"""

from .scoring import score_routes
from .weights import (
    DEFAULT_WEIGHTS,
    FACTORS,
    PREFERENCE_PRESETS,
    VALID_PREFERENCES,
    normalize_weights,
    resolve_weights,
)

__all__ = [
    "score_routes",
    "DEFAULT_WEIGHTS",
    "FACTORS",
    "PREFERENCE_PRESETS",
    "VALID_PREFERENCES",
    "normalize_weights",
    "resolve_weights",
]
