# Database Design

GoRoute uses **SQLite** — a single file database, zero configuration, ideal for
a 3-hour hackathon MVP. The schema is deliberately simple: flat tables with
foreign keys and a few indexes. No ORM complexity is required; a lightweight
SQL layer (e.g., `sqlite3` or SQLAlchemy) is sufficient.

**Design principles**

- Every user-owned row carries a `user_id` foreign key.
- IDs are integer primary keys (autoincrement).
- Timestamps are stored as ISO-8601 UTC text (`YYYY-MM-DDTHH:MM:SSZ`).
- Scores are stored as REAL in the range 0–100.
- Complex/nested data (e.g., route legs) is stored as JSON text in a single
  column to keep the schema flat.

---

## Entity Relationship Overview

```
User 1───N SavedPlace
User 1───N DailyCommute
User 1───N Journey 1───N Route
User 1───N Booking   (Booking N───1 Route, optional)
User 1───N Notification
```

---

## 1. User

Stores an authenticated account.

| Field          | Type    | Notes                                  |
| -------------- | ------- | -------------------------------------- |
| `id`           | INTEGER | **PK**, autoincrement                  |
| `name`         | TEXT    | Display name                           |
| `email`        | TEXT    | **Unique**, login identifier           |
| `password_hash`| TEXT    | Hashed password (never plain text)     |
| `preference`   | TEXT    | Default preference (fastest/cheapest/…)|
| `created_at`   | TEXT    | ISO-8601 UTC                           |
| `updated_at`   | TEXT    | ISO-8601 UTC                           |

**Relationships:** One user has many SavedPlaces, DailyCommutes, Journeys,
Bookings, Notifications.

**Indexes:** Unique index on `email`.

---

## 2. SavedPlace

A frequently used location for quick journey entry.

| Field        | Type    | Notes                                     |
| ------------ | ------- | ----------------------------------------- |
| `id`         | INTEGER | **PK**, autoincrement                     |
| `user_id`    | INTEGER | **FK → User.id**                          |
| `label`      | TEXT    | e.g., "Home", "Work"                      |
| `address`    | TEXT    | Human-readable address                    |
| `latitude`   | REAL    | Coordinate                                |
| `longitude`  | REAL    | Coordinate                                |
| `created_at` | TEXT    | ISO-8601 UTC                              |

**Relationships:** Many SavedPlaces belong to one User.

**Indexes:** Index on `user_id`.

---

## 3. DailyCommute

A recurring commute the user wants planned automatically.

| Field             | Type    | Notes                                        |
| ----------------- | ------- | -------------------------------------------- |
| `id`              | INTEGER | **PK**, autoincrement                        |
| `user_id`         | INTEGER | **FK → User.id**                             |
| `source_label`    | TEXT    | e.g., "Home"                                 |
| `source_lat`      | REAL    | Coordinate                                   |
| `source_lng`      | REAL    | Coordinate                                   |
| `dest_label`      | TEXT    | e.g., "Work"                                 |
| `dest_lat`        | REAL    | Coordinate                                   |
| `dest_lng`        | REAL    | Coordinate                                   |
| `departure_time`  | TEXT    | Preferred departure (e.g., "09:00")          |
| `days_of_week`    | TEXT    | CSV, e.g., "Mon,Tue,Wed,Thu,Fri"             |
| `preference`      | TEXT    | fastest/cheapest/least_walking/most_reliable |
| `is_active`       | INTEGER | 0/1 boolean                                  |
| `created_at`      | TEXT    | ISO-8601 UTC                                 |
| `updated_at`      | TEXT    | ISO-8601 UTC                                 |

**Relationships:** Many DailyCommutes belong to one User.

**Indexes:** Index on `user_id`; composite index on `(user_id, is_active)`.

---

## 4. Journey

A single journey request (a search) made by the user.

| Field            | Type    | Notes                                       |
| ---------------- | ------- | ------------------------------------------- |
| `id`             | INTEGER | **PK**, autoincrement                       |
| `user_id`        | INTEGER | **FK → User.id**                            |
| `source_label`   | TEXT    | Origin label                                |
| `source_lat`     | REAL    | Coordinate                                  |
| `source_lng`     | REAL    | Coordinate                                  |
| `dest_label`     | TEXT    | Destination label                           |
| `dest_lat`       | REAL    | Coordinate                                  |
| `dest_lng`       | REAL    | Coordinate                                  |
| `departure_time` | TEXT    | Requested departure                         |
| `preference`     | TEXT    | User preference used for scoring            |
| `status`         | TEXT    | planned / active / completed / cancelled    |
| `selected_route_id` | INTEGER | **FK → Route.id** (nullable)             |
| `created_at`     | TEXT    | ISO-8601 UTC                                |

**Relationships:** One Journey belongs to one User and has many Routes. The
selected route is referenced by `selected_route_id`.

**Indexes:** Index on `user_id`; index on `(user_id, created_at)` for history.

---

## 5. Route

A single candidate route produced for a Journey, including its score.

| Field              | Type    | Notes                                     |
| ------------------ | ------- | ----------------------------------------- |
| `id`               | INTEGER | **PK**, autoincrement                     |
| `journey_id`       | INTEGER | **FK → Journey.id**                       |
| `mode_summary`     | TEXT    | e.g., "Metro → Auto"                      |
| `legs_json`        | TEXT    | JSON array of legs (mode, from, to, ...)  |
| `total_duration_min`| INTEGER| Travel time in minutes                    |
| `total_cost`       | REAL    | Estimated cost                            |
| `waiting_time_min` | INTEGER | Total waiting time                        |
| `transfers`        | INTEGER | Number of transfers                       |
| `walking_distance_m`| INTEGER| Walking distance in metres                |
| `reliability`      | REAL    | 0–1 reliability estimate                  |
| `score`            | REAL    | 0–100 engine score                        |
| `is_selected`      | INTEGER | 0/1 whether this was chosen               |
| `created_at`       | TEXT    | ISO-8601 UTC                              |

**Relationships:** Many Routes belong to one Journey. A Route may be referenced
by Bookings.

**Indexes:** Index on `journey_id`; index on `(journey_id, score)` for ranking.

---

## 6. Booking

A reservation for a bookable leg of a chosen route.

| Field          | Type    | Notes                                        |
| -------------- | ------- | -------------------------------------------- |
| `id`           | INTEGER | **PK**, autoincrement                        |
| `user_id`      | INTEGER | **FK → User.id**                             |
| `route_id`     | INTEGER | **FK → Route.id** (nullable)                 |
| `provider`     | TEXT    | e.g., cab/auto provider                      |
| `status`       | TEXT    | pending / confirmed / cancelled              |
| `fare`         | REAL    | Fare amount                                  |
| `scheduled_at` | TEXT    | Pickup time                                  |
| `details_json` | TEXT    | Provider response / extra details (JSON)     |
| `created_at`   | TEXT    | ISO-8601 UTC                                 |

**Relationships:** Many Bookings belong to one User; optionally linked to a
Route.

**Indexes:** Index on `user_id`; index on `(user_id, created_at)`.

---

## 7. Notification

An event message shown to the user.

| Field        | Type    | Notes                                          |
| ------------ | ------- | ---------------------------------------------- |
| `id`         | INTEGER | **PK**, autoincrement                          |
| `user_id`    | INTEGER | **FK → User.id**                               |
| `type`       | TEXT    | route_change / reminder / booking_update       |
| `title`      | TEXT    | Short title                                    |
| `message`    | TEXT    | Body text                                      |
| `is_read`    | INTEGER | 0/1 boolean                                    |
| `created_at` | TEXT    | ISO-8601 UTC                                   |

**Relationships:** Many Notifications belong to one User.

**Indexes:** Index on `(user_id, is_read)`; index on `(user_id, created_at)`.

---

## Notes for Implementation

- Enable `PRAGMA foreign_keys = ON;` per connection in SQLite.
- Keep the schema in a single `schema.sql` (or a single migrations module) for
  Phase 2 — no migration framework needed for the MVP.
- Store route legs and provider details as JSON text to avoid extra tables.
- All timestamps UTC; convert for display in the frontend.
