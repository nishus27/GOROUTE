# GoRoute Frontend

React + TypeScript + Vite single-page application.

**Status:** Placeholder (Phase 0). The app is scaffolded in **Phase 3 — Frontend
Foundation**. No `package.json` or source files exist yet, by design.

## Intended Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/             # Images, icons, styles
│   ├── components/         # Reusable UI components (AppShell, NotificationBell, ...)
│   ├── pages/              # Route-level pages (see docs/UI_PAGES.md)
│   ├── services/           # API client modules (fetch wrapper + per-domain clients)
│   ├── hooks/              # Custom React hooks (useAuth, ...)
│   ├── types/              # TypeScript types/interfaces (Route, Journey, ...)
│   ├── utils/              # Formatting/helpers
│   ├── App.tsx             # Root component (Phase 3)
│   └── main.tsx            # Entry point (Phase 3)
├── index.html              # Vite HTML entry (Phase 3)
├── package.json            # Dependencies & scripts (Phase 3)
├── tsconfig.json           # TypeScript config (Phase 3)
└── vite.config.ts          # Vite config (Phase 3)
```

## Planned Scripts (Phase 3)

```bash
npm install
npm run dev      # start dev server (http://localhost:5173)
npm run build    # production build
npm run preview  # preview the production build
```

## Environment

- `VITE_API_BASE_URL` — backend base URL (e.g., `http://localhost:5000`).
- `VITE_GOOGLE_MAPS_API_KEY` — public, restricted browser key (Phase 6).

See [`../docs/ENVIRONMENT.md`](../docs/ENVIRONMENT.md) and
[`../docs/UI_PAGES.md`](../docs/UI_PAGES.md).
