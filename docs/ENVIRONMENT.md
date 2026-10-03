# Environment

GoRoute reads configuration from environment variables. A template lives at the
repository root: [`.env.example`](../.env.example). **Never commit real
secrets.** Copy the template to `.env` locally and fill in your own values.

```bash
cp .env.example .env
```

> **Rule:** `.env` is git-ignored. `.env.example` must contain placeholders only
> — never real keys.

---

## Backend (Flask)

These are read server-side only. They must never be exposed to the browser.

| Variable           | Required | Example                    | Purpose                                            |
| ------------------ | -------- | -------------------------- | -------------------------------------------------- |
| `FLASK_ENV`        | No       | `development`              | Flask environment mode                             |
| `FLASK_DEBUG`      | No       | `1`                        | Enable debug reloader                              |
| `SECRET_KEY`       | Yes      | `some-random-secret`       | Session/token signing; generate randomly           |
| `PORT`             | No       | `5000`                     | Dev server port                                    |
| `DATABASE_URL`     | Yes      | `sqlite:///goroute.db`     | SQLite database location                           |
| `OPENAI_API_KEY`   | Yes*     | `sk-...`                   | OpenAI explanations/personalization (Phase 9)      |
| `OPENAI_MODEL`     | No       | `gpt-4o-mini`              | Model used for explanations                        |
| `GOOGLE_MAPS_API_KEY` | Yes*  | `AIza...`                  | Google Maps route/mapping data (Phase 6)           |

\* Required only when the corresponding feature is enabled. The app should
**degrade gracefully** (with a clear error or fallback) when a key is missing,
so the MVP can be demoed without live keys.

---

## Frontend (Vite)

Vite only exposes variables prefixed with `VITE_` to the browser. **Only public
values belong here.** Never place the OpenAI key or a server-only Google key in
a `VITE_*` variable.

| Variable                   | Required | Example                  | Purpose                                        |
| -------------------------- | -------- | ------------------------ | ---------------------------------------------- |
| `VITE_API_BASE_URL`        | Yes      | `http://localhost:5000`  | Backend API base URL                           |
| `VITE_GOOGLE_MAPS_API_KEY` | Optional | `AIza...`                | Public browser key for rendering maps (Phase 6) |

### Notes on the Google Maps keys

- If Google Maps is called **from the backend**, use `GOOGLE_MAPS_API_KEY`
  (server-side, unrestricted-to-your-server) and never expose it.
- If maps are rendered **in the browser**, a separate, **restricted public key**
  (`VITE_GOOGLE_MAPS_API_KEY`) is required. Restrict it by HTTP referrer in the
  Google Cloud console.
- These are two different keys with different restrictions — do not reuse one
  for both purposes.

---

## How to Generate a `SECRET_KEY`

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the result into `SECRET_KEY` in your local `.env`.

---

## Local Development Ports

| Service  | Default URL              |
| -------- | ------------------------ |
| Frontend | `http://localhost:5173`  |
| Backend  | `http://localhost:5000`  |

The backend must allow the frontend origin via CORS (Phase 1). During local
development the frontend reads `VITE_API_BASE_URL` to reach the backend.

---

## Safety Checklist

- [ ] `.env` exists locally and is **not** committed.
- [ ] `.env.example` contains placeholders only.
- [ ] No key is hardcoded anywhere in `frontend/` or `backend/` source.
- [ ] Only `VITE_*` values reach the browser.
- [ ] Public Google Maps keys are restricted by HTTP referrer.
- [ ] `SECRET_KEY` is randomly generated, not a default string.
