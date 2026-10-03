# GoRoute Backend

Python + Flask REST API.

**Status:** Phase 1 (Backend Foundation) is **DONE**. The API foundation —
app factory, SQLite database, session auth, and a health endpoint — is
implemented and covered by tests.

## Structure

```
backend/
├── app/
│   ├── __init__.py         # Flask app factory + error handlers
│   ├── config.py           # Configuration from environment variables
│   ├── extensions.py       # Shared SQLAlchemy (db) + CORS instances
│   ├── routes/             # HTTP layer (health, auth, ...)
│   │   ├── __init__.py     # Blueprint registration (mounted at /api)
│   │   ├── health.py       # GET /api/health
│   │   └── auth.py         # signup / login / logout / me
│   ├── services/           # Orchestration & business logic (later phases)
│   ├── engine/             # Deterministic scoring/decision engine (later)
│   ├── models/             # SQLite models (User, ...)
│   ├── integrations/       # Google Maps + OpenAI clients (later phases)
│   └── utils/              # Responses, validation, session auth helpers
├── instance/               # SQLite DB lives here (git-ignored)
├── tests/                  # Backend tests (pytest)
├── .env.example            # Environment template (placeholders only)
├── requirements.txt        # Python dependencies
└── run.py                  # Dev entry point
```

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate         # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env         # then edit values as needed
python run.py                  # serves http://localhost:5000
```

The SQLite database (`backend/instance/goroute.db`) is created automatically on
first start.

## Tests

```bash
cd backend
.venv\Scripts\python.exe -m pytest tests -v
```

## Implemented Endpoints

| Method | Path | Auth |
| ------ | ---- | ---- |
| GET | `/api/health` | — |
| POST | `/api/auth/signup` | — |
| POST | `/api/auth/login` | — |
| POST | `/api/auth/logout` | — |
| GET | `/api/auth/me` | 🔒 |

Auth is **session-cookie based** for the MVP: the browser sends the session
cookie automatically. Cross-origin requests must include credentials (e.g. a
Vite dev proxy from `/api` to `http://localhost:5000` is recommended).

## Key Rules

- The **decision engine** owns the numeric route score. OpenAI never scores.
- Google Maps only provides route/mapping data.
- All secrets (`SECRET_KEY`, `OPENAI_API_KEY`, `GOOGLE_MAPS_API_KEY`) stay
  server-side in `backend/.env` and are never committed.

See [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md),
[`../docs/API_DESIGN.md`](../docs/API_DESIGN.md), and
[`../docs/DATABASE_DESIGN.md`](../docs/DATABASE_DESIGN.md).
