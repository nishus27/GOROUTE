# Development Phases

The implementation roadmap for GoRoute. Each phase lists its **Goal**, **Files
likely to change**, **Dependencies**, **Expected result**, and **Testing
requirements**. Phases are sequential; do not start a phase before its
dependencies are complete.

> **Current phase:** Phase 0 (Project Foundation). See
> [`../PROJECT_STATUS.md`](../PROJECT_STATUS.md).

---

## Phase 0 — Project Foundation and Documentation

**Goal:** Create the repository structure and all documentation. No feature code.

**Files likely to change:**
- `README.md`, `PROJECT_STATUS.md`, `.gitignore`, `.env.example`
- `docs/*.md` (all 9 documents)
- Folder skeleton under `frontend/`, `backend/`, `docs/`

**Dependencies:** None.

**Expected result:** A documented, empty project skeleton that another agent can
pick up and implement phase by phase.

**Testing requirements:** Verify the folder tree matches the docs; verify every
documented file exists; verify no secrets are committed.

---

## Phase 1 — Backend Foundation

**Goal:** Stand up a runnable Flask API with a health endpoint and config from
environment variables.

**Files likely to change:**
- `backend/run.py`, `backend/config.py`, `backend/requirements.txt`
- `backend/app/__init__.py` (app factory)
- `backend/app/routes/__init__.py` (blueprint registration)
- `backend/.gitignore`

**Dependencies:** Phase 0.

**Expected result:** `python run.py` starts a Flask server; `GET /api/health`
returns `{ "status": "ok" }`; CORS allows the Vite dev origin; config reads from
`.env`.

**Testing requirements:** Start the server; curl `/api/health`; confirm it
returns 200 JSON; confirm missing env vars fail loudly.

---

## Phase 2 — Database

**Goal:** Create the SQLite schema and data-access layer for all entities.

**Files likely to change:**
- `backend/app/models/` (models or a `schema.sql` + access functions)
- `backend/app/__init__.py` (DB init on startup)
- `backend/config.py` (`DATABASE_URL`)
- `backend/tests/` (schema tests)

**Dependencies:** Phase 1.

**Expected result:** The DB file is created on first run with all tables
(`User`, `SavedPlace`, `DailyCommute`, `Journey`, `Route`, `Booking`,
`Notification`), foreign keys enforced, and CRUD helpers available.

**Testing requirements:** Verify all tables/columns/indexes exist; test insert +
select round-trips for each entity; verify foreign keys are enforced.

---

## Phase 3 — Frontend Foundation

**Goal:** Stand up a React + TypeScript + Vite app with routing, layout, and an
API client.

**Files likely to change:**
- `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts`
- `frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/App.tsx`
- `frontend/src/components/` (AppShell/NavBar), `frontend/src/services/api.ts`
- `frontend/src/types/`, `frontend/src/hooks/`, `frontend/src/index.css`

**Dependencies:** Phase 1 (for the API base URL contract).

**Expected result:** `npm run dev` serves the app; a shell/nav renders; the API
client can call `/api/health`.

**Testing requirements:** Build succeeds (`npm run build`); app renders with no
console errors; a test call to `/api/health` succeeds from the browser.

---

## Phase 4 — Authentication

**Goal:** Implement signup, login, logout end to end.

**Files likely to change:**
- `backend/app/routes/auth.py`, `backend/app/services/auth_service.py`
- `backend/app/models/user.py`, `backend/app/utils/` (hashing, auth guard)
- `frontend/src/pages/Login.tsx`, `frontend/src/pages/Signup.tsx`
- `frontend/src/services/auth.ts`, `frontend/src/hooks/useAuth.ts`

**Dependencies:** Phases 1–3.

**Expected result:** Users can sign up, log in, and log out; protected endpoints
reject unauthenticated requests.

**Testing requirements:** Test signup with duplicate email (rejected), login
with wrong password (rejected), successful login returns a token, and protected
routes return 401 without a token.

---

## Phase 5 — Journey Planner

**Goal:** Accept a journey request and return candidate routes (initially from
mock/stub data) with scores.

**Files likely to change:**
- `backend/app/routes/routes.py`, `backend/app/services/journey_service.py`
- `backend/app/models/journey.py`, `backend/app/models/route.py`
- `frontend/src/pages/PlanJourney.tsx`, `frontend/src/pages/RouteResults.tsx`
- `frontend/src/services/journey.ts`, `frontend/src/types/route.ts`

**Dependencies:** Phases 2, 4.

**Expected result:** Submitting the plan form returns a ranked list of candidate
routes persisted as a Journey + Routes.

**Testing requirements:** Validate required fields; verify a Journey and its
Routes are persisted; verify the results page renders the ranked list.

---

## Phase 6 — Google Maps / Route Data

**Goal:** Replace mock candidates with real route data from Google Maps.

**Files likely to change:**
- `backend/app/integrations/google_maps.py`
- `backend/app/services/journey_service.py` (use the integration)
- `backend/config.py` (`GOOGLE_MAPS_API_KEY`)
- `frontend/src/components/MapView.tsx` (display geometry)

**Dependencies:** Phase 5.

**Expected result:** Candidate routes come from Google Maps across requested
modes, with duration/distance/geometry/traffic where available.

**Testing requirements:** Test with a real key and with a missing key (graceful
error); verify mapping of API responses into Route metrics; verify MapView
renders a polyline.

---

## Phase 7 — Decision Engine

**Goal:** Implement the deterministic scoring engine and wire it into journey
search.

**Files likely to change:**
- `backend/app/engine/` (`scoring.py`, `normalize.py`, `weights.py`)
- `backend/app/services/scoring_service.py`
- `backend/app/routes/routes.py` (`/api/routes/score`)
- `backend/tests/test_engine.py`

**Dependencies:** Phase 5 (candidate routes), Phase 6 (real data optional).

**Expected result:** Every route gets a 0–100 score; routes are ranked; the best
route is selected and stored. Scoring is deterministic.

**Testing requirements:** Unit tests for normalization (including the
max == min case), the worked example from
[`ROUTE_DECISION_ENGINE.md`](./ROUTE_DECISION_ENGINE.md), tie-breaking, and
determinism (same input → same output).

---

## Phase 8 — Dynamic Rerouting

**Goal:** Recalculate routes when conditions change and detect a changed
recommendation.

**Files likely to change:**
- `backend/app/services/reroute_service.py`
- `backend/app/routes/routes.py` (`/api/routes/reroute`)
- `backend/app/models/notification.py` (emit on change)
- `frontend/src/pages/RouteResults.tsx` (reroute button/state)

**Dependencies:** Phases 6, 7.

**Expected result:** A reroute re-runs the engine, compares to the previous best,
and returns `changed: true|false` with a reason.

**Testing requirements:** Simulate changed metrics → verify the recommendation
can change; verify `changed: false` when metrics are unchanged; verify a
notification is created on change.

---

## Phase 9 — OpenAI Explanation

**Goal:** Explain the engine's decision in natural language.

**Files likely to change:**
- `backend/app/integrations/openai_client.py`
- `backend/app/services/ai_service.py`
- `backend/app/routes/ai.py` (`/api/ai/explain-route`)
- `frontend/src/components/RecommendedRouteCard.tsx`

**Dependencies:** Phases 7, 8.

**Expected result:** The results page shows a human-readable explanation of the
selected route. OpenAI receives the already-computed decision and never scores.

**Testing requirements:** Verify the prompt includes the scored routes and
selected route; verify a missing API key degrades gracefully (fallback text);
verify the numeric score is never produced by the AI path.

---

## Phase 10 — Dashboard

**Goal:** Build the home screen summarizing today's commute and recent activity.

**Files likely to change:**
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/components/CommuteCard.tsx`, `RecentJourneysList.tsx`
- `frontend/src/services/` (daily commute, journeys, notifications, insights)

**Dependencies:** Phases 4, 5, 7, 9 (data sources).

**Expected result:** The dashboard shows today's recommended route with score,
recent journeys, and a notification preview.

**Testing requirements:** Verify empty states (new user) and populated states;
verify cards link to the correct pages; verify no crash when data is missing.

---

## Phase 11 — Daily Commute

**Goal:** Let users configure a recurring commute and see today's recommendation.

**Files likely to change:**
- `backend/app/routes/daily_commute.py`
- `backend/app/services/daily_commute_service.py`
- `backend/app/models/daily_commute.py`
- `frontend/src/pages/DailyCommute.tsx`, `frontend/src/services/dailyCommute.ts`

**Dependencies:** Phases 2, 4, 5, 7.

**Expected result:** Users can create/update an active commute and view today's
recommended route for it.

**Testing requirements:** Create + update + fetch a commute; verify only active
commutes drive today's recommendation; verify ownership checks.

---

## Phase 12 — Saved Places and Notifications

**Goal:** Manage saved places and display notifications.

**Files likely to change:**
- `backend/app/routes/saved_places.py`, `backend/app/models/saved_place.py`
- `backend/app/routes/notifications.py`, `backend/app/models/notification.py`
- `backend/app/services/notification_service.py`
- `frontend/src/pages/SavedPlaces.tsx`
- `frontend/src/components/NotificationBell.tsx`, `NotificationPanel.tsx`

**Dependencies:** Phases 2, 4, 8.

**Expected result:** Full CRUD for saved places; a notification bell with unread
count and a panel listing notifications.

**Testing requirements:** CRUD round-trip for saved places with ownership checks;
verify reroute changes create notifications; verify unread count updates.

---

## Phase 13 — Journey History

**Goal:** Let users browse past journeys and the routes compared.

**Files likely to change:**
- `backend/app/routes/journeys.py`
- `frontend/src/pages/JourneyHistory.tsx`
- `frontend/src/components/JourneyDetailPanel.tsx`

**Dependencies:** Phases 2, 4, 5.

**Expected result:** A chronological list of past journeys with a detail view
showing compared routes and scores.

**Testing requirements:** Verify history is scoped to the user and ordered
newest-first; verify the detail view shows all compared routes.

---

## Phase 14 — Booking

**Goal:** Let users book a bookable leg of a chosen route and view booking
history.

**Files likely to change:**
- `backend/app/routes/bookings.py`, `backend/app/services/booking_service.py`
- `backend/app/models/booking.py`
- `frontend/src/pages/Booking.tsx`, `frontend/src/pages/BookingHistory.tsx`
- `frontend/src/services/bookings.ts`

**Dependencies:** Phases 2, 4, 5 (chosen route), 12 (notifications).

**Expected result:** Users can create a booking (status pending/confirmed) and
see past/upcoming bookings with cancel.

**Testing requirements:** Create + list bookings scoped to the user; verify
status transitions; verify a booking notification is emitted; mock the external
provider if used.

---

## Phase 15 — Weekly Insights

**Goal:** Aggregate the past 7 days into a weekly summary.

**Files likely to change:**
- `backend/app/routes/insights.py`
- `backend/app/services/insights_service.py`
- `frontend/src/pages/WeeklyInsights.tsx`
- `frontend/src/components/InsightCards.tsx`, `ModeBreakdownChart.tsx`

**Dependencies:** Phases 2, 4, 13 (history), optionally 9 (narrative summary).

**Expected result:** `/api/weekly-insights` returns totals and a mode breakdown;
the page renders cards and a chart.

**Testing requirements:** Verify aggregation over a seeded 7-day window; verify
empty-week handling; verify totals match the underlying journeys.

---

## Phase 16 — Integration Testing and Polish

**Goal:** Harden the whole system end to end and polish the UX.

**Files likely to change:**
- `backend/tests/*` (integration tests)
- `frontend/src/**` (empty states, loading, error handling, responsive layout)
- `README.md`, `docs/*` (keep in sync with implementation)
- `PROJECT_STATUS.md` (mark phases complete)

**Dependencies:** All previous phases.

**Expected result:** A working MVP with a full end-to-end flow: sign up → plan a
journey → get a scored recommendation + explanation → reroute → save → view
history/insights.

**Testing requirements:** Run the full backend test suite; run `npm run build`;
walk through the end-to-end user flow manually; verify no secrets are committed;
verify graceful degradation when Google Maps / OpenAI keys are absent.

---

## Phase Summary

| Phase | Name | Key Deliverable |
| ----- | ---- | --------------- |
| 0 | Project Foundation | Structure + docs |
| 1 | Backend Foundation | Runnable Flask API |
| 2 | Database | SQLite schema + access |
| 3 | Frontend Foundation | Runnable Vite app + API client |
| 4 | Authentication | Signup/login/logout |
| 5 | Journey Planner | Route search + results (mock data) |
| 6 | Google Maps | Real route data |
| 7 | Decision Engine | Deterministic 0–100 scoring |
| 8 | Dynamic Rerouting | Recalculation + change detection |
| 9 | OpenAI | Explanations (never scores) |
| 10 | Dashboard | Home summary |
| 11 | Daily Commute | Recurring commute |
| 12 | Saved Places + Notifications | CRUD + alerts |
| 13 | Journey History | Past journeys |
| 14 | Booking | Book + history |
| 15 | Weekly Insights | Weekly aggregation |
| 16 | Testing + Polish | End-to-end hardening |

