# API Design

The GoRoute backend exposes a **REST/JSON API** served by Flask. All endpoints
are prefixed with `/api`. This document defines the planned endpoints and the
responsibility of each request and response.

> **Status:** Phase 1 implements the **Health** and **Authentication** endpoints
> below. All other endpoints remain design-only until their phase. Paths and
> responsibilities are the contract other agents should follow.

## Conventions

- **Base URL:** `http://localhost:5000/api` (dev). Frontend uses
  `VITE_API_BASE_URL`.
- **Format:** JSON request and response bodies.
- **Auth:** Session cookie (MVP). The browser sends the session cookie
  automatically, so the frontend must call the API with credentials included.
  Endpoints marked 🔒 require an active session. (A future phase may add
  `Authorization: Bearer <token>` support.)
- **Errors:** Standard shape
  ```json
  { "error": { "code": "VALIDATION_ERROR", "message": "source is required" } }
  ```
- **Timestamps:** ISO-8601 UTC.
- **Scores:** numbers in the range 0–100.

---

## Health

| Method | Path | Auth | Responsibility |
| ------ | ---- | ---- | -------------- |
| GET | `/api/health` | — | Liveness probe |

**Response `200`:** `{ "status": "ok", "service": "goroute" }`

---

## Authentication

| Method | Path | Auth | Responsibility |
| ------ | ---- | ---- | -------------- |
| POST | `/api/auth/signup` | — | Create a user account |
| POST | `/api/auth/login` | — | Verify credentials, start a session |
| POST | `/api/auth/logout` | — | Invalidate the current session |
| GET | `/api/auth/me` | 🔒 | Return the current user |

### POST `/api/auth/signup`

**Request**
```json
{ "name": "Asha", "email": "asha@example.com", "password": "secret123" }
```
**Response `201`**
```json
{ "user": { "id": 1, "name": "Asha", "email": "asha@example.com" } }
```
**Responsibilities:** Validate input, ensure unique email, hash password, create
`User`, start a session (session cookie).

### POST `/api/auth/login`

**Request:** `{ "email": "...", "password": "..." }`
**Response `200`:** `{ "user": {...} }`
**Responsibilities:** Verify password hash, start a session (session cookie).

### POST `/api/auth/logout`

**Request:** empty.
**Response `200`:** `{ "success": true }`
**Responsibilities:** Invalidate the session/token.

### GET `/api/auth/me`  🔒

**Response `200`:** `{ "user": { "id": 1, "name": "Asha", "email": "asha@example.com" } }`
**Responsibilities:** Return the currently authenticated user from the session.

---

## Journey

| Method | Path | Auth | Responsibility |
| ------ | ---- | ---- | -------------- |
| POST | `/api/routes/search` | 🔒 | Fetch candidate routes for a request |
| POST | `/api/routes/score` | 🔒 | Score/rank supplied candidate routes |
| POST | `/api/routes/reroute` | 🔒 | Recalculate for changed conditions |

### POST `/api/routes/search`

**Request**
```json
{
  "source": { "label": "Home", "lat": 19.07, "lng": 72.87 },
  "destination": { "label": "Work", "lat": 19.11, "lng": 72.86 },
  "departure_time": "2026-10-03T09:00:00Z",
  "preference": "fastest",
  "modes": ["train", "metro", "bus", "cab", "auto", "walk"]
}
```
**Response `200`**
```json
{
  "journey_id": 42,
  "routes": [
    {
      "id": 101, "mode_summary": "Metro → Auto", "score": 87.4,
      "metrics": {
        "total_duration_min": 38, "total_cost": 65.0, "waiting_time_min": 6,
        "transfers": 1, "walking_distance_m": 350, "reliability": 0.9
      },
      "legs": [ ... ], "is_selected": true
    }
  ],
  "recommended_route_id": 101
}
```
**Responsibilities:** Validate request, call Google Maps for candidate routes,
invoke the decision engine, persist `Journey` + `Route` rows, return scored and
ranked routes.

### POST `/api/routes/score`

**Request:** candidate routes + metrics + optional weights/preference.
**Response `200`:** the same routes with `score`, normalized metrics, and a
`ranked` ordering.
**Responsibilities:** Pure decision-engine call — normalize, weight, score,
rank. No external APIs.

### POST `/api/routes/reroute`

**Request:** `{ "journey_id": 42, "reason": "traffic", "now": "..." }`
**Response `200`:** updated routes, `recommended_route_id`, and
`changed: true|false` with a `change_reason`.
**Responsibilities:** Re-fetch candidates, re-run the engine, compare to the
previous best, and report any change.

---

## AI

| Method | Path | Auth | Responsibility |
| ------ | ---- | ---- | -------------- |
| POST | `/api/ai/explain-route` | 🔒 | Explain the engine's decision |

### POST `/api/ai/explain-route`

**Request**
```json
{ "journey_id": 42, "route_id": 101, "preference": "fastest" }
```
**Response `200`**
```json
{ "explanation": "This route is fastest and reliable, with only one transfer..." }
```
**Responsibilities:** Send the *already-computed* scored routes and the
selected route to OpenAI, return a human-readable explanation. **OpenAI never
computes the score.**

---

## Saved Places

| Method | Path | Auth | Responsibility |
| ------ | ---- | ---- | -------------- |
| GET | `/api/saved-places` | 🔒 | List the user's saved places |
| POST | `/api/saved-places` | 🔒 | Create a saved place |
| PUT | `/api/saved-places/:id` | 🔒 | Update a saved place |
| DELETE | `/api/saved-places/:id` | 🔒 | Delete a saved place |

**POST request**
```json
{ "label": "Home", "address": "Andheri", "latitude": 19.07, "longitude": 72.87 }
```
**GET response `200`:** `{ "saved_places": [ { "id": 1, "label": "Home", ... } ] }`

**Responsibilities:** CRUD scoped to the authenticated user. Ownership must be
checked on `:id` operations.

---

## Daily Commute

| Method | Path | Auth | Responsibility |
| ------ | ---- | ---- | -------------- |
| GET | `/api/daily-commute` | 🔒 | Get the user's commute(s) |
| POST | `/api/daily-commute` | 🔒 | Create a daily commute |
| PUT | `/api/daily-commute` | 🔒 | Update the user's commute |

**POST request**
```json
{
  "source": { "label": "Home", "lat": 19.07, "lng": 72.87 },
  "destination": { "label": "Work", "lat": 19.11, "lng": 72.86 },
  "departure_time": "09:00", "days_of_week": "Mon,Tue,Wed,Thu,Fri",
  "preference": "fastest", "is_active": true
}
```
**GET response `200`:** the commute definition plus today's recommended route.

**Responsibilities:** Persist commute preferences; expose today's recommended
route for the dashboard.

---

## History

| Method | Path | Auth | Responsibility |
| ------ | ---- | ---- | -------------- |
| GET | `/api/journeys` | 🔒 | List past journeys (history) |
| POST | `/api/journeys` | 🔒 | Save/record a journey |

**GET response `200`:** `{ "journeys": [ { "id": 42, "source_label": "Home",
"dest_label": "Work", "created_at": "...", "selected_route_id": 101 } ] }`

**Responsibilities:** Return the user's journey history, newest first, with
pagination-ready structure.

---

## Bookings

| Method | Path | Auth | Responsibility |
| ------ | ---- | ---- | -------------- |
| GET | `/api/bookings` | 🔒 | List bookings (history) |
| POST | `/api/bookings` | 🔒 | Create a booking |

**POST request**
```json
{ "route_id": 101, "provider": "cab", "scheduled_at": "2026-10-03T09:00:00Z" }
```
**POST response `201`:** the created booking with `status`.

**Responsibilities:** Create and list bookings scoped to the user; update status
and emit a Notification.

---

## Notifications

| Method | Path | Auth | Responsibility |
| ------ | ---- | ---- | -------------- |
| GET | `/api/notifications` | 🔒 | List notifications |

**GET response `200`:** `{ "notifications": [ { "id": 1, "type":
"route_change", "title": "...", "message": "...", "is_read": false,
"created_at": "..." } ] }`

**Responsibilities:** Return notifications for the user (newest first). A
future `PUT /api/notifications/:id/read` may be added; not required for the MVP.

---

## Weekly

| Method | Path | Auth | Responsibility |
| ------ | ---- | ---- | -------------- |
| GET | `/api/weekly-insights` | 🔒 | Weekly commute summary |

**GET response `200`**
```json
{
  "period": { "from": "...", "to": "..." },
  "total_time_min": 320, "total_cost": 540.0, "journeys": 10,
  "mode_breakdown": { "metro": 6, "auto": 4 }, "route_changes": 3,
  "summary": "You saved 40 minutes this week by taking the metro..."
}
```
**Responsibilities:** Aggregate the past 7 days of journeys/bookings into
insights; optionally add a narrative summary via OpenAI.

---

## Endpoint Summary

| Area | Endpoints |
| ---- | --------- |
| Health | GET health |
| Auth | POST signup, login, logout; GET me |
| Journey | POST routes/search, routes/score, routes/reroute |
| AI | POST ai/explain-route |
| Saved Places | GET/POST/PUT/DELETE saved-places |
| Daily Commute | GET/POST/PUT daily-commute |
| History | GET/POST journeys |
| Bookings | GET/POST bookings |
| Notifications | GET notifications |
| Weekly | GET weekly-insights |

