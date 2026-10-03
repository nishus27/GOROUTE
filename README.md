# GoRoute

**GoRoute is a decision layer for multimodal commuting.**

GoRoute is an intelligent multimodal commute decision platform. A user enters a
source, destination, departure time, and travel preference. GoRoute compares
transportation options (Local Train, Metro, Bus, Cab, Auto, Walking, and
multimodal combinations), evaluates them against objective factors, and
recommends the best route using a **deterministic scoring engine**.

> GoRoute is **not** a replacement for Google Maps. Google Maps provides
> route/mapping data; GoRoute makes the numerical route decision and explains it.

---

## Status

**Phase 0 — Project Foundation — IN PROGRESS**

This repository currently contains only the project foundation: folder
structure and documentation. No application features are implemented yet.
See [`PROJECT_STATUS.md`](./PROJECT_STATUS.md) for the phase tracker and
[`docs/DEVELOPMENT_PHASES.md`](./docs/DEVELOPMENT_PHASES.md) for the roadmap.

---

## Tech Stack (MVP)

| Layer     | Technology                  | Why                                             |
| --------- | --------------------------- | ----------------------------------------------- |
| Frontend  | React + TypeScript + Vite   | Fast dev server, typed UI, quick to build       |
| Backend   | Python + Flask              | Minimal boilerplate, fast to iterate in a hackathon |
| Database  | SQLite                      | Zero-setup file DB, ideal for a 3-hour MVP      |
| Routing   | Google Maps APIs            | Route/geometry/traffic data                     |
| Explain   | OpenAI API                  | Human-readable explanations & personalization   |

This is the preferred stack and was chosen as-is for a 3-hour hackathon MVP.

---

## Repository Layout

```
GOROUTE/
├── frontend/        # React + TypeScript + Vite single-page app
├── backend/         # Python + Flask REST API
├── docs/            # Project documentation (read this first)
├── .env.example     # Environment variable template (no secrets)
├── .gitignore
├── README.md
└── PROJECT_STATUS.md
```

See [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) for the full architecture.

---

## Documentation Index

| Document | Contents |
| -------- | -------- |
| [`docs/PROJECT_OVERVIEW.md`](./docs/PROJECT_OVERVIEW.md) | Purpose, problem, solution, users, stack |
| [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) | Component responsibilities & data flow |
| [`docs/FEATURES.md`](./docs/FEATURES.md) | Full feature list with I/O and dependencies |
| [`docs/DATABASE_DESIGN.md`](./docs/DATABASE_DESIGN.md) | SQLite schema & entities |
| [`docs/API_DESIGN.md`](./docs/API_DESIGN.md) | Planned REST endpoints |
| [`docs/UI_PAGES.md`](./docs/UI_PAGES.md) | Planned frontend pages |
| [`docs/ROUTE_DECISION_ENGINE.md`](./docs/ROUTE_DECISION_ENGINE.md) | Deterministic scoring system |
| [`docs/DEVELOPMENT_PHASES.md`](./docs/DEVELOPMENT_PHASES.md) | Phase 0–16 roadmap |
| [`docs/ENVIRONMENT.md`](./docs/ENVIRONMENT.md) | Environment variables |

---

## Getting Started

> Nothing runs yet — this is Phase 0. Setup commands for the frontend and
> backend are documented here and will be implemented in Phase 1 and Phase 3.

**1. Configure environment**

```bash
cp .env.example .env   # then fill in your local values
```

**2. Backend (Phase 1)**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate         # Windows PowerShell
pip install -r requirements.txt
python run.py
```

**3. Frontend (Phase 3)**

```bash
cd frontend
npm install
npm run dev
```

---

## Guiding Principles

1. Keep the architecture simple — a single Flask API, not microservices.
2. The **decision engine** owns the numerical route score. OpenAI never scores.
3. Google Maps provides data; GoRoute provides the decision.
4. No secrets in the repository. Ever.
5. Optimized for a 3-hour hackathon MVP, then extended phase by phase.
