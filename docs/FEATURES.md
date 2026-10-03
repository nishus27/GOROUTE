# Features

This document lists every planned GoRoute feature with its **Purpose**, **Main
Inputs**, **Main Outputs**, and **Dependencies**.

> **Status:** None of these features are implemented yet. This is the Phase 0
> specification. Each feature is built in the phase listed in
> [`DEVELOPMENT_PHASES.md`](./DEVELOPMENT_PHASES.md).

---

## 1. Authentication

**Purpose:** Identify the user so their places, preferences, commutes, history,
and bookings are private and personalized.

**Main inputs:**
- Signup: name, email, password.
- Login: email, password.
- Session/token from the client on subsequent requests.

**Main outputs:**
- Created user record (hashed password).
- Auth token/session for the client.
- Current-user profile for the frontend.

**Dependencies:** Database (`User`), backend API (`/api/auth/*`), frontend
Login/Signup pages. No external APIs.

---

## 2. Dashboard

**Purpose:** Give the user a single home screen summarizing their commute at a
glance — today's recommended route, upcoming commute, recent journeys, and
notifications.

**Main inputs:**
- Authenticated user id.
- Daily commute configuration.
- Recent journeys, notifications, weekly insight summary.

**Main outputs:**
- Today's recommended route card with score.
- Quick "Plan a journey" entry point.
- Recent activity and notification preview.

**Dependencies:** Authentication, Journey Planner (data), Daily Commute,
Journey History, Notifications, Decision Engine results.

---

## 3. Journey Planner

**Purpose:** Let the user enter a journey request and get scored route
recommendations.

**Main inputs:**
- Source (place/coordinates).
- Destination (place/coordinates).
- Departure time.
- Travel preference (e.g., fastest, cheapest, least walking, most reliable).

**Main outputs:**
- A list of candidate routes with metrics and scores.
- The recommended (highest-scoring) route.
- Explanation of the recommendation.

**Dependencies:** Authentication, Google Maps Integration, Route Decision
Engine, OpenAI Explanation, Database (`Journey`, `Route`).

---

## 4. Multimodal Route Comparison

**Purpose:** Compare options across Local Train, Metro, Bus, Cab, Auto, Walking,
and multimodal combinations side by side.

**Main inputs:**
- Candidate routes (with mode composition, legs, durations, costs, transfers).
- User preference weights.

**Main outputs:**
- Normalized comparison table/list of all modes.
- Per-factor breakdown (time, cost, walking, transfers, waiting, reliability).
- Highlighted best option per factor.

**Dependencies:** Google Maps Integration, Route Decision Engine, Journey
Planner.

---

## 5. Route Decision Engine

**Purpose:** Deterministically compute a 0–100 score for each candidate route,
rank them, and select the best one according to preference weights.

**Main inputs:**
- Candidate routes with raw metrics (travel time, cost, waiting, transfers,
  walking distance, reliability).
- Preference weights (defaults: Time 30, Reliability 20, Cost 15, Waiting 10,
  Transfers 10, Walking 15).

**Main outputs:**
- Normalized metrics per route.
- Weighted score (0–100) per route.
- Ranked list and the selected best route.

**Dependencies:** Journey Planner / Google Maps data. No external AI — this is
pure deterministic code.

---

## 6. Dynamic Rerouting

**Purpose:** Detect changing conditions and recalculate, recommending a
different route when appropriate.

**Main inputs:**
- Active journey/route.
- Current time and (if available) updated traffic/delay data.
- Reroute trigger (timer, condition change, or user action).

**Main outputs:**
- Recalculated candidate routes and new scores.
- Either "no change" or a new recommended route with a reason.
- Optional notification when the recommendation changes.

**Dependencies:** Google Maps Integration, Route Decision Engine, Journey
Planner, Notifications.

---

## 7. Google Maps Integration

**Purpose:** Supply the route/mapping data that the decision engine evaluates.
Google Maps **provides data**; GoRoute **makes the decision**.

**Main inputs:**
- Origin, destination, departure time, requested travel modes.
- API key (`GOOGLE_MAPS_API_KEY`, backend-side).

**Main outputs:**
- Candidate routes with distance, duration, traffic duration, geometry,
  transit/leg details.

**Dependencies:** Google Maps APIs, backend `integrations/` client. No
decision logic here.

---

## 8. OpenAI Explanation

**Purpose:** Explain the engine's decision in plain language and personalize the
wording to the user's preference. **OpenAI never computes the score.**

**Main inputs:**
- The engine's scored, ranked routes and the selected best route.
- The user's stated preference and relevant history/context.

**Main outputs:**
- A short human-readable explanation of why the route was recommended.
- Optional trade-off summary and personalization notes.

**Dependencies:** Route Decision Engine (for the decision to explain),
Authentication (for personalization), OpenAI API
(`OPENAI_API_KEY`, backend-side).

---

## 9. Daily Commute

**Purpose:** Let the user save their recurring commute once and get it planned
and re-evaluated automatically, day after day.

**Main inputs:**
- Source, destination, preferred departure time, days, preference.
- Active/inactive flag.

**Main outputs:**
- A stored commute definition.
- Today's recommended route for that commute (with score).
- Optional alerts when the recommended route changes.

**Dependencies:** Authentication, Database (`DailyCommute`), Journey Planner,
Route Decision Engine, Notifications.

---

## 10. Saved Places

**Purpose:** Let users store frequently used locations (Home, Work, etc.) for
fast journey entry.

**Main inputs:**
- Label (e.g., Home, Work), address, coordinates.

**Main outputs:**
- CRUD-managed list of saved places.
- Quick-select options in the Journey Planner.

**Dependencies:** Authentication, Database (`SavedPlace`).

---

## 11. Notifications

**Purpose:** Inform the user about important events — a changed recommendation,
a commute reminder, or a booking update.

**Main inputs:**
- Events emitted by rerouting, daily commute, or bookings.
- User id.

**Main outputs:**
- Notification records (type, message, timestamp, read/unread).
- A notification panel / badge in the UI.

**Dependencies:** Authentication, Database (`Notification`), Dynamic Rerouting,
Daily Commute, Booking.

---

## 12. Journey History

**Purpose:** Let users review past journeys, the routes compared, and which
route was chosen.

**Main inputs:**
- Journey searches performed by the user.
- Chosen route and scores.

**Main outputs:**
- Chronological list of past journeys.
- Detail view of a past journey's compared routes.

**Dependencies:** Authentication, Database (`Journey`, `Route`), Journey
Planner, Decision Engine.

---

## 13. Booking

**Purpose:** Let the user book or reserve a bookable leg (e.g., a cab/auto or a
reservable transit seat) for a chosen route.

**Main inputs:**
- Chosen route and the leg to book.
- Passenger/user details and requested time.

**Main outputs:**
- A booking record with status (pending, confirmed, cancelled).
- Booking confirmation details.

**Dependencies:** Authentication, Database (`Booking`), Journey Planner
(chosen route), Notifications. External booking providers may be mocked in the
MVP.

---

## 14. Booking History

**Purpose:** Let users review their past and upcoming bookings.

**Main inputs:**
- User id.
- Booking records.

**Main outputs:**
- Chronological list of bookings with status.
- Booking detail view and cancel action.

**Dependencies:** Authentication, Database (`Booking`), Booking.

---

## 15. Weekly Insights

**Purpose:** Summarize the user's commuting week — time spent, money spent,
modes used, and how often the recommendation changed.

**Main inputs:**
- Journey history over the past 7 days.
- Bookings and routes chosen.

**Main outputs:**
- Aggregated metrics (total time, total cost, mode breakdown, transfer counts).
- A short narrative summary (optionally via OpenAI).

**Dependencies:** Authentication, Database (`Journey`, `Route`, `Booking`),
Journey History, optionally OpenAI Explanation.

---

## Feature Dependency Summary

| Feature | Depends on |
| ------- | ---------- |
| Authentication | Database, Backend API |
| Dashboard | Auth, Journey Planner, Daily Commute, History, Notifications |
| Journey Planner | Auth, Google Maps, Decision Engine, OpenAI, Database |
| Multimodal Comparison | Google Maps, Decision Engine, Journey Planner |
| Route Decision Engine | Google Maps data (no AI) |
| Dynamic Rerouting | Google Maps, Decision Engine, Notifications |
| Google Maps Integration | Google Maps APIs |
| OpenAI Explanation | Decision Engine, Auth, OpenAI API |
| Daily Commute | Auth, Database, Journey Planner, Decision Engine, Notifications |
| Saved Places | Auth, Database |
| Notifications | Auth, Database, Rerouting, Daily Commute, Booking |
| Journey History | Auth, Database, Journey Planner |
| Booking | Auth, Database, Journey Planner, Notifications |
| Booking History | Auth, Database, Booking |
| Weekly Insights | Auth, Database, Journey History, (optional OpenAI) |


