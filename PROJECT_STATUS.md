# Project Status

**Project:** GoRoute — intelligent multimodal commute decision platform
**Current phase:** Phase 1 — Backend Foundation (DONE)

This file is the single source of truth for build progress. Update it as each
phase completes. See [`docs/DEVELOPMENT_PHASES.md`](./docs/DEVELOPMENT_PHASES.md)
for phase details.

---

## Phase Tracker

| Phase | Name | Status |
| ----- | ---- | ------ |
| 0  | Project Foundation | **DONE** |
| 1  | Backend Foundation | **DONE** |
| 2  | Database | NOT STARTED |
| 3  | Frontend Foundation | NOT STARTED |
| 4  | Authentication | NOT STARTED |
| 5  | Journey Planner | NOT STARTED |
| 6  | Google Maps | NOT STARTED |
| 7  | Decision Engine | NOT STARTED |
| 8  | Dynamic Rerouting | NOT STARTED |
| 9  | OpenAI | NOT STARTED |
| 10 | Dashboard | NOT STARTED |
| 11 | Daily Commute | NOT STARTED |
| 12 | Saved Places + Notifications | NOT STARTED |
| 13 | History | NOT STARTED |
| 14 | Booking | NOT STARTED |
| 15 | Weekly Insights | NOT STARTED |
| 16 | Testing + Polish | NOT STARTED |

Status values: `NOT STARTED` · `IN PROGRESS` · `BLOCKED` · `DONE`.

---

## Phase 0 — Project Foundation

**Status:** DONE

**Completed in this phase:**
- [x] Inspected the workspace (was empty).
- [x] Created the root structure: `frontend/`, `backend/`, `docs/`.
- [x] Created internal frontend folders (React + TS + Vite layout).
- [x] Created internal backend folders (Flask layout).
- [x] Created root files: `.gitignore`, `.env.example`, `README.md`.
- [x] Created all 9 documentation files in `docs/`.
- [x] Created `PROJECT_STATUS.md`.

**Not done (intentionally — later phases):**
- [ ] No application code (no Flask app, no React app).
- [ ] No login, dashboard, journey planner, Google Maps, OpenAI, scoring
      engine, rerouting, booking, or notifications.
- [ ] No dependencies installed.

**Next up:** Phase 1 — Backend Foundation. **DONE** (see below).

---

## Phase 1 — Backend Foundation

**Status:** DONE

**Completed in this phase:**
- [x] `backend/requirements.txt` — Flask, Flask-SQLAlchemy, Flask-Cors,
      python-dotenv, Werkzeug, pytest.
- [x] `backend/app/config.py` — env-driven config; SQLite at
      `backend/instance/goroute.db`; CORS origins; session settings.
- [x] `backend/app/extensions.py` — shared `db` (SQLAlchemy) and `cors` instances.
- [x] `backend/app/__init__.py` — app factory: init extensions, register
      blueprints, JSON error handlers, auto-create the SQLite DB/tables.
- [x] `backend/app/models/user.py` — `User` (id, name, unique email,
      `password_hash`, `created_at`) with Werkzeug password hashing.
- [x] `backend/app/routes/health.py` — `GET /api/health` →
      `{ "status": "ok", "service": "goroute" }`.
- [x] `backend/app/routes/auth.py` — `POST /api/auth/signup`,
      `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`.
- [x] `backend/app/utils/` — response envelope, validation, session auth guard.
- [x] `backend/run.py` — dev entry point (default `http://localhost:5000`).
- [x] `backend/.env.example` — placeholders only (no real secrets).
- [x] `backend/tests/` — health, signup, login, duplicate-email, validation,
      session/`me`, and logout tests. **10 tests, all passing.**
- [x] `docs/API_DESIGN.md` updated to match the implemented auth/health contract.

**Decisions / deviations from the design docs:**
- Auth is **session-cookie based** (not bearer tokens), as chosen for the MVP.
  Signup/login return `{ "user": {...} }` with no `token` field.
- `GET /api/auth/me` was added (not in the original design) to let the frontend
  restore the current user from the session.
- `POST /api/auth/logout` is idempotent (no 401 when already logged out).

**Not done (intentionally — later phases):**
- [ ] No route search/scoring, Google Maps, OpenAI, decision engine, rerouting,
      dashboard, saved places, history, booking, or notifications.
- [ ] No frontend code (Phase 3+).

**Next up:** Phase 2 — Database (do not start automatically).

---

## Conventions / Decisions

- **Stack:** React + TypeScript + Vite (frontend), Python + Flask (backend),
  SQLite (database). Chosen for a 3-hour hackathon MVP; no alternative stack.
- **Architecture:** Single Flask API (no microservices), one SQLite file.
- **Decision ownership:** The deterministic engine computes the score; OpenAI
  only explains; Google Maps only provides data.
- **Secrets:** Never committed; `.env` is git-ignored; `.env.example` has
  placeholders only.
- **Auth:** Session-cookie based for the MVP (see `docs/API_DESIGN.md`).

---

## Change Log

| Date | Phase | Note |
| ---- | ----- | ---- |
| 2026-10-03 | 0 | Initial project structure and documentation created. |
| 2026-10-03 | 1 | Backend foundation: Flask app factory, SQLite, session auth, health endpoint, 10 passing tests. |
