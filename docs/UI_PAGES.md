# UI Pages

This document describes the planned frontend pages for GoRoute (React +
TypeScript + Vite). Each page lists its **Purpose**, **Main Components**,
**User Actions**, and **Backend APIs Required**.

> **Status:** Design only — not implemented. Pages are built in Phase 3 onward.
> Suggested routing paths are shown in the heading of each page.

---

## 1. Login (`/login`)

**Purpose:** Authenticate an existing user.

**Main components:** `LoginForm` (email, password), submit button, error banner,
link to Signup.

**User actions:** Enter credentials, submit, navigate to Dashboard on success.

**Backend APIs required:** `POST /api/auth/login`

---

## 2. Signup (`/signup`)

**Purpose:** Create a new user account.

**Main components:** `SignupForm` (name, email, password), submit button,
validation messages, link to Login.

**User actions:** Enter details, submit, auto-login and navigate to Dashboard.

**Backend APIs required:** `POST /api/auth/signup`

---

## 3. Dashboard (`/`)

**Purpose:** Home screen summarizing the user's commute at a glance.

**Main components:** `CommuteCard` (today's recommended route + score),
`QuickPlanForm` entry, `RecentJourneysList`, `NotificationBell`/panel,
`InsightsTeaser`.

**User actions:** View today's recommendation, start a new journey, open
notifications, open history/insights.

**Backend APIs required:** `GET /api/daily-commute`, `GET /api/journeys`,
`GET /api/notifications`, `GET /api/weekly-insights`

---

## 4. Plan Journey (`/plan`)

**Purpose:** Collect the journey request (source, destination, departure time,
preference).

**Main components:** `PlaceInput` (with saved-place quick select),
`DepartureTimePicker`, `PreferenceSelector`, `ModeSelector`, `PlanButton`.

**User actions:** Enter/select source and destination, set departure time and
preference, optionally restrict modes, submit to get results.

**Backend APIs required:** `GET /api/saved-places` (quick select),
`POST /api/routes/search`

---

## 5. Route Results (`/results`)

**Purpose:** Present scored, ranked route options and the recommendation.

**Main components:** `RecommendedRouteCard` (score + explanation),
`RouteList` (all candidates with scores), `RouteComparisonTable`,
`FactorBreakdown`, `MapView` (Google Maps), `RerouteButton`.

**User actions:** Compare routes, view factor breakdown, read the explanation,
select a route, request a reroute, start a booking.

**Backend APIs required:** `POST /api/routes/search`,
`POST /api/routes/score`, `POST /api/ai/explain-route`,
`POST /api/routes/reroute`

---

## 6. Daily Commute (`/daily-commute`)

**Purpose:** Configure and review the user's recurring commute.

**Main components:** `CommuteForm` (source, destination, departure time, days,
preference, active toggle), `TodayRecommendationCard`.

**User actions:** Create/update the commute, toggle active, view today's
recommended route.

**Backend APIs required:** `GET /api/daily-commute`,
`POST /api/daily-commute`, `PUT /api/daily-commute`

---

## 7. Saved Places (`/saved-places`)

**Purpose:** Manage frequently used locations.

**Main components:** `SavedPlacesList`, `SavedPlaceForm` (label, address,
coordinates), edit/delete controls.

**User actions:** Add, edit, delete saved places.

**Backend APIs required:** `GET /api/saved-places`, `POST /api/saved-places`,
`PUT /api/saved-places/:id`, `DELETE /api/saved-places/:id`

---

## 8. Journey History (`/history`)

**Purpose:** Review past journeys and the routes compared.

**Main components:** `JourneyHistoryList` (date, source → destination, chosen
route), `JourneyDetailPanel` (compared routes + scores).

**User actions:** Browse history, open a journey detail, re-run a past journey.

**Backend APIs required:** `GET /api/journeys`

---

## 9. Bookings (`/bookings/new`)

**Purpose:** Book a bookable leg of a chosen route.

**Main components:** `BookingForm` (provider, time, details), `FareSummary`,
`ConfirmButton`.

**User actions:** Choose a bookable leg, enter details, confirm a booking.

**Backend APIs required:** `POST /api/bookings`

---

## 10. Booking History (`/bookings`)

**Purpose:** Review past and upcoming bookings.

**Main components:** `BookingList` (provider, status, fare, time),
`BookingDetailPanel`, `CancelButton`.

**User actions:** Browse bookings, open a booking, cancel a booking.

**Backend APIs required:** `GET /api/bookings`

---

## 11. Weekly Insights (`/insights`)

**Purpose:** Show a summary of the user's commuting week.

**Main components:** `InsightCards` (total time, total cost, journeys),
`ModeBreakdownChart`, `SummaryText` (OpenAI narrative).

**User actions:** View the weekly summary and mode breakdown.

**Backend APIs required:** `GET /api/weekly-insights`

---

## 12. Notifications (`/notifications` and panel)

**Purpose:** Show route-change alerts, reminders, and booking updates.

**Main components:** `NotificationBell` (badge with unread count),
`NotificationPanel`/`NotificationList` (type, title, message, time, read state).

**User actions:** Open the panel, read notifications, follow a route-change
notification to Route Results.

**Backend APIs required:** `GET /api/notifications`

---

## 13. Profile (`/profile`)

**Purpose:** View and update the user's basic profile and default preference.

**Main components:** `ProfileForm` (name, email, default preference),
`LogoutButton`.

**User actions:** Update profile/preference, log out.

**Backend APIs required:** `POST /api/auth/logout` (and a future
`GET/PUT /api/profile` — not required for the MVP; profile fields may be read
from the login/signup response).

---

## Route Map Summary

| Path | Page |
| ---- | ---- |
| `/login` | Login |
| `/signup` | Signup |
| `/` | Dashboard |
| `/plan` | Plan Journey |
| `/results` | Route Results |
| `/daily-commute` | Daily Commute |
| `/saved-places` | Saved Places |
| `/history` | Journey History |
| `/bookings/new` | Booking |
| `/bookings` | Booking History |
| `/insights` | Weekly Insights |
| `/notifications` | Notifications |
| `/profile` | Profile |

**Shared components (Phase 3+):** `AppShell`/`NavBar`, `NotificationBell`,
`LoadingSpinner`, `ErrorBanner`, `ScoreBadge`, `ModeIcon`, `MapView`.

