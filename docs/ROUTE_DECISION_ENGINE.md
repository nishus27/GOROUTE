# Route Decision Engine

The Route Decision Engine is the **core of GoRoute**. It is a **deterministic,
rule-based scoring system** that turns candidate routes into a ranked list and
selects the best route for the user's stated preference.

> **Critical rule:** **OpenAI must NOT calculate the numerical route score.**
> The scoring engine owns the numerical decision. OpenAI only *explains* the
> decision the engine already made. Google Maps only *provides route data*.

## Responsibilities

1. Receive candidate routes (from Google Maps / mock data).
2. Normalize each route's metrics across the candidate set.
3. Apply preference weights.
4. Calculate a **0–100 score** for every route.
5. Rank routes by score (descending).
6. Select the highest-scoring route as the recommendation.

## Scoring Factors

| Factor            | Meaning                                             | Direction |
| ----------------- | --------------------------------------------------- | --------- |
| Travel Time       | Total in-vehicle time in minutes                    | Lower better |
| Reliability       | Likelihood the route runs on time (0–1)             | Higher better |
| Cost              | Estimated fare/cost                                 | Lower better |
| Waiting Time      | Time spent waiting (transfers, boarding) in minutes | Lower better |
| Transfers         | Number of mode changes                              | Lower better |
| Walking Distance  | Total walking distance in metres                    | Lower better |

## Default Weights

| Factor           | Default Weight |
| ---------------- | -------------- |
| Travel Time      | **30%**        |
| Reliability      | **20%**        |
| Cost             | **15%**        |
| Waiting Time     | **10%**        |
| Transfers        | **10%**        |
| Walking Distance | **15%**        |
| **Total**        | **100%**       |

Weights are configurable per request via the user's preference. The defaults
above apply when no preference override is supplied. Weights must always sum to
1.0 (normalize if they do not).

## Algorithm

```
function scoreRoutes(candidates, weights = DEFAULT_WEIGHTS):
    if candidates is empty: return []

    # 1. Normalize each metric to a 0..1 "goodness" value across candidates.
    for each factor in [time, reliability, cost, waiting, transfers, walking]:
        values = [route.metric(factor) for route in candidates]
        for each route in candidates:
            route.norm[factor] = normalize(factor, route.metric(factor), values)

    # 2. Apply weights and compute a 0..100 score.
    for each route in candidates:
        raw = Σ (weights[factor] * route.norm[factor])   # raw in 0..1
        route.score = round(raw * 100, 1)

    # 3. Rank descending by score (stable tie-break, see below).
    ranked = sort(candidates by score desc)

    # 4. Mark the winner.
    ranked[0].is_selected = true
    return ranked
```

## Normalization

Each metric is converted to a **0–1 "goodness" score** where 1 is best.

- **Lower-is-better** (time, cost, waiting, transfers, walking):
  ```
  goodness = (max - value) / (max - min)
  ```
- **Higher-is-better** (reliability):
  ```
  goodness = (value - min) / (max - min)
  ```
- **Degenerate case:** if `max == min` for a factor, set `goodness = 1.0` for
  all routes (the factor cannot discriminate, so it must not penalize anyone).

This min–max normalization makes factors with different units (minutes, rupees,
metres, counts) comparable.

## Determinism & Tie-Breaking

- Same inputs **must** always produce the same scores and ranking.
- No randomness, no clock dependence, no AI in the score path.
- **Tie-break order** when scores are equal: (1) higher score, (2) lower
  `total_duration_min`, (3) lower `total_cost`, (4) lower `transfers`,
  (5) lower `id`. This guarantees a stable, reproducible winner.

## Worked Example

Two candidates, default weights:

| Route | Time(min) | Reliability | Cost | Waiting | Transfers | Walking(m) |
| ----- | --------- | ----------- | ---- | ------- | --------- | ---------- |
| A     | 40        | 0.8         | 60   | 5       | 1         | 400        |
| B     | 30        | 0.6         | 90   | 8       | 2         | 200        |

Normalized goodness (min–max across the two):

| Factor (weight)  | A    | B    |
| ---------------- | ---- | ---- |
| Time (0.30)      | 0.00 | 1.00 |
| Reliability(0.20)| 1.00 | 0.00 |
| Cost (0.15)      | 1.00 | 0.00 |
| Waiting (0.10)   | 1.00 | 0.00 |
| Transfers (0.10) | 1.00 | 0.00 |
| Walking (0.15)   | 0.00 | 1.00 |

- **A** = 0.30·0 + 0.20·1 + 0.15·1 + 0.10·1 + 0.10·1 + 0.15·0 = **0.55 → 55.0**
- **B** = 0.30·1 + 0.20·0 + 0.15·0 + 0.10·0 + 0.10·0 + 0.15·1 = **0.45 → 45.0**

**Result:** Route A wins (55.0) because the user's default weights favor
reliability, cost, waiting, and transfers, even though B is faster.

## Preference Presets

A preference is a named weight set. Suggested presets:

| Preference       | Emphasis                                        |
| ---------------- | ----------------------------------------------- |
| `fastest`        | Travel Time ↑ (e.g., 0.50), others reduced      |
| `cheapest`       | Cost ↑ (e.g., 0.40), others reduced             |
| `least_walking`  | Walking Distance ↑ (e.g., 0.40), others reduced |
| `most_reliable`  | Reliability ↑ (e.g., 0.40), others reduced      |
| `balanced`       | The default weights above                       |

Preset weight sets live in the engine as plain configuration. They must sum to
1.0 after normalization.

## Engine Contract

**Input**
```json
{
  "preference": "balanced",
  "weights": { "time": 0.3, "reliability": 0.2, "cost": 0.15,
               "waiting": 0.1, "transfers": 0.1, "walking": 0.15 },
  "routes": [
    { "id": 101, "total_duration_min": 40, "reliability": 0.8, "total_cost": 60,
      "waiting_time_min": 5, "transfers": 1, "walking_distance_m": 400 }
  ]
}
```

**Output**
```json
{
  "ranked": [
    { "id": 101, "score": 55.0, "is_selected": true,
      "normalized": { "time": 0.0, "reliability": 1.0, "cost": 1.0,
                      "waiting": 1.0, "transfers": 1.0, "walking": 0.0 } }
  ],
  "recommended_route_id": 101
}
```

## Rerouting

Rerouting **reuses the same engine**. It does not score differently:

1. Re-fetch candidate routes with updated conditions.
2. Run `scoreRoutes` again.
3. Compare the new `recommended_route_id` to the previous one.
4. If different, report `changed: true` with a reason (e.g., "traffic increased
   travel time on the metro").
5. Optionally emit a Notification and ask OpenAI to explain *what changed*.

## Where This Lives in the Code

- `backend/app/engine/` — the deterministic scoring implementation
  (e.g., `normalize.py`, `scoring.py`, `weights.py`).
- Called by `backend/app/services/` (JourneyService, RerouteService).
- **Never** called by, or replaced by, OpenAI. OpenAI is downstream of the
  engine and consumes its output.
