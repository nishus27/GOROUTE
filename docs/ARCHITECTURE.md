# Architecture

## Overview

GoRoute is a simple **client → API → services → data/external APIs** layered
application. It is intentionally **not** microservices: one Flask API process
serves all endpoints, and one SQLite file stores all data.

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React + TS + Vite)           │
│  Pages · Components · API client · Local UI state           │
└───────────────────────────┬─────────────────────────────────┘
                            │  REST / JSON  (VITE_API_BASE_URL)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API (Flask)                     │
│  Routes/Controllers · Request validation · Auth · JSON I/O   │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         Services                             │
│  JourneyService · ScoringService · RerouteService ·          │
│  AIService · BookingService · NotificationService ·          │
│  InsightsService                                             │
└───────────┬───────────────────────────────┬─────────────────┘
            ▼                               ▼
┌───────────────────────────┐   ┌─────────────────────────────┐
│   Database (SQLite)       │   │      External APIs           │
│   Users · Places ·        │   │  Google Maps (routes/data)   │
│   Routes · Journeys ·     │   │  OpenAI (explanations only)  │
│   Bookings · Notifications│   └─────────────────────────────┘
└───────────────────────────┘
```

## Layer Responsibilities

### Frontend (React + TypeScript + Vite)

**Responsible for:**

- Rendering pages and components (Login, Dashboard, Plan Journey, Route
  Results, Daily Commute, Saved Places, History, Bookings, Insights,
  Notifications, Profile).
- Collecting user input: source, destination, departure time, preference.
- Calling the backend REST API via a typed API client.
- Holding **UI state only** (form values, loading, errors, selected route).
- Displaying scores, route options, and OpenAI explanations returned by the
  backend.

**Not responsible for:**

- Any scoring/decision logic (that lives in the backend engine).
- Storing API keys for OpenAI (only public `VITE_*` keys may reach the browser).
- Persisting application data (that is the database's job).

### Backend API (Flask)

**Responsible for:**

- Exposing the REST endpoints defined in [`API_DESIGN.md`](./API_DESIGN.md).
- Validating and normalizing request payloads.
- Authentication and session/token handling.
- Orchestrating services (journey planning, scoring, rerouting, AI, booking).
- Serializing responses to JSON.
- Owning all secrets (`OPENAI_API_KEY`, `GOOGLE_MAPS_API_KEY`) — server-side only.

**Not responsible for:**

- Rendering UI.
- Computing route geometry itself (delegated to Google Maps).
- Generating numeric scores from AI (that is the engine's job).

### Database (SQLite)

**Responsible for:**

- Persisting users, saved places, daily commutes, journeys, routes, bookings,
  and notifications.
- Providing fast lookups for a single-user-per-session MVP.
- Being simple, file-based, and zero-configuration.

See [`DATABASE_DESIGN.md`](./DATABASE_DESIGN.md) for entities and indexes.

### Google Maps

**Responsible for:**

- Providing **route/mapping information**: routes between two points across
  modes, distance, duration, geometry/polyline, and (where available) traffic
  duration and transit details.
- Serving as the **source of candidate routes** for the decision engine.

**Not responsible for:**

- Deciding which route is best for the user. Google Maps *provides data*;
  GoRoute *makes the decision*.

### OpenAI

**Responsible for:**

- Generating **human-readable explanations** of the engine's decision.
- **Personalization** of wording/tone to the user's preference and history.
- Optionally summarizing trade-offs in natural language.

**Not responsible for:**

- Computing the numeric route score. **OpenAI must never calculate the score.**
- Selecting the winning route. The engine selects; OpenAI explains.

### Decision Engine

**Responsible for:**

- Receiving candidate routes with metrics.
- Normalizing metrics across candidates.
- Applying preference weights (Travel Time 30%, Reliability 20%, Cost 15%,
  Waiting 10%, Transfers 10%, Walking 15% by default).
- Calculating a **0–100 score** per route.
- Ranking routes and selecting the highest-scoring one.
- Being **deterministic**: identical inputs always produce identical scores.

See [`ROUTE_DECISION_ENGINE.md`](./ROUTE_DECISION_ENGINE.md).

### Rerouting

**Responsible for:**

- Detecting when conditions change (traffic, delay, departure time shift,
  user action).
- Re-fetching candidate routes and re-running the decision engine.
- Comparing the new best route to the previous recommendation.
- Returning a changed recommendation (with reason) when the best route differs.

**Not responsible for:**

- Inventing scores or overriding the engine. Rerouting re-invokes the engine.

## Data Flow: Plan a Journey

```
1. User submits source, destination, departure time, preference   (Frontend)
2. Frontend → POST /api/routes/search                             (API)
3. JourneyService requests candidate routes                       (Service)
4. Google Maps returns routes + metrics                           (External)
5. ScoringService normalizes + scores + ranks candidates          (Engine)
6. AIService asks OpenAI to explain the winning route             (External)
7. Backend persists the search as a Journey                       (Database)
8. Backend returns scored, ranked routes + explanation            (API → Frontend)
9. Frontend renders Route Results with score and reason           (Frontend)
```

## Data Flow: Dynamic Reroute

```
1. Trigger: timer, condition change, or explicit user action
2. RerouteService re-fetches candidate routes (Google Maps)
3. ScoringService re-scores and re-ranks (Engine)
4. If new best route ≠ previous best → flag a changed recommendation
5. AIService explains what changed (OpenAI)
6. Result surfaced via API and/or Notification
```

## Key Architectural Rules

1. **Google Maps provides route/mapping information.**
2. **GoRoute's scoring engine makes the numerical route decision.**
3. **OpenAI explains the decision.** OpenAI never scores.
4. **One backend process, one database file.** No microservices.
5. **Secrets stay on the backend.** Only public `VITE_*` keys reach the browser.
6. **Determinism:** same inputs → same score, always.

## Backend Internal Structure

```
backend/
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── routes/             # API blueprints/controllers (HTTP layer)
│   ├── services/           # Orchestration + business logic
│   ├── engine/             # Deterministic scoring/decision engine
│   ├── models/             # SQLite models / data access
│   ├── integrations/       # Google Maps + OpenAI clients
│   └── utils/              # Shared helpers (validation, errors, time)
├── tests/                  # Backend tests
├── config.py               # Configuration from environment
├── requirements.txt        # Python dependencies (Phase 1)
└── run.py                  # Dev entry point (Phase 1)
```

## Frontend Internal Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/             # Images, icons, styles
│   ├── components/         # Reusable UI components
│   ├── pages/              # Route-level pages (see UI_PAGES.md)
│   ├── services/           # API client modules
│   ├── hooks/              # Custom React hooks
│   ├── types/              # TypeScript types/interfaces
│   ├── utils/              # Formatting/helpers
│   ├── App.tsx             # Root component (Phase 3)
│   └── main.tsx            # Entry point (Phase 3)
├── index.html              # Vite HTML entry (Phase 3)
├── package.json            # Frontend deps/scripts (Phase 3)
├── tsconfig.json           # TypeScript config (Phase 3)
└── vite.config.ts          # Vite config (Phase 3)
```
