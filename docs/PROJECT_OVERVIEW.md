# Project Overview

## Project Name

**GoRoute**

## Purpose

GoRoute is an **intelligent multimodal commute decision platform**. A user enters
a source, destination, departure time, and a travel preference. GoRoute compares
transportation options — Local Train, Metro, Bus, Cab, Auto, Walking, and
multimodal combinations — and recommends the best route for that specific
journey.

**Core positioning: GoRoute is a decision layer for multimodal commuting.**

GoRoute sits *on top of* existing map/routing providers. It does not try to be a
map. It consumes route data and turns it into a clear, personalized,
explainable recommendation.

> GoRoute is **not** a replacement for Google Maps.

## Problem

Commuters in dense cities face a fragmented choice:

- Many transport modes exist (train, metro, bus, cab, auto, walking), each with
  its own app, fare rules, and reliability profile.
- Comparing options is manual and guesswork-driven.
- "Fastest" is not always "best": cost, transfers, walking distance, waiting
  time, traffic, and reliability all matter and vary by user and by time of day.
- A route that was good yesterday may be bad today because of traffic, delays,
  or crowding.
- Map apps show routes but do not make a *personalized decision* for the user's
  stated preference, and they do not explain *why* one option beats another.

## Solution

GoRoute provides a single decision surface:

1. The user states a **source, destination, departure time, and preference**
   (e.g., cheapest, fastest, least walking, most reliable).
2. GoRoute gathers **candidate routes** across all modes, including multimodal
   combinations, using Google Maps routing data where available.
3. A **deterministic decision engine** normalizes route metrics, applies
   preference weights, computes a **0–100 score** for each candidate, ranks them,
   and selects the best one.
4. **OpenAI** generates a plain-language explanation of the decision and
   personalizes the wording — it never computes the numeric score.
5. If conditions change (traffic, delays, departure time), GoRoute
   **recalculates** and may recommend a different route.

The result is a transparent, reproducible recommendation with a clear reason.

## Target Users

- **Daily city commuters** choosing between train, metro, bus, and last-mile
  options every day.
- **Cost-conscious travelers** who want the cheapest acceptable route.
- **Time-sensitive travelers** who want the fastest reliable route.
- **Accessibility / low-walking users** who want to minimize walking and
  transfers.
- **Occasional travelers** unfamiliar with a city who need a trustworthy,
  explained recommendation.
- **Students and professionals** with a fixed daily commute (Daily Commute).

## Core Value Proposition

> **GoRoute turns scattered transport options into one explainable, personalized
> route decision.**

- **Decision, not just directions** — a scored recommendation, not a raw list.
- **Multimodal by default** — mixes train + metro + auto + walking in one route.
- **Personalized** — weights reflect the user's stated preference.
- **Explainable** — every recommendation comes with a human-readable reason.
- **Adaptive** — recalculates and can change its mind when conditions change.
- **Deterministic & auditable** — the same inputs produce the same score.

## Main Features

See [`FEATURES.md`](./FEATURES.md) for full detail. High level:

1. Authentication
2. Dashboard
3. Journey Planner
4. Multimodal Route Comparison
5. Route Decision Engine
6. Dynamic Rerouting
7. Google Maps Integration
8. OpenAI Explanation
9. Daily Commute
10. Saved Places
11. Notifications
12. Journey History
13. Booking
14. Booking History
15. Weekly Insights

## Technology Stack

| Layer            | Technology                       | Rationale                                     |
| ---------------- | -------------------------------- | --------------------------------------------- |
| Frontend         | React + TypeScript + Vite        | Fast HMR, typed components, quick MVP build   |
| Backend          | Python + Flask                   | Minimal boilerplate, easy REST, fast to write |
| Database         | SQLite                           | Zero-setup file DB, perfect for a hackathon   |
| Mapping/Routing  | Google Maps APIs                 | Route, geometry, distance, traffic data       |
| Explanation / AI | OpenAI API                       | Explanations & personalization only           |
| Decision         | In-house deterministic engine    | Owns the numeric route score                  |

The preferred stack was adopted without changes; it is well suited to a
3-hour hackathon MVP and simple to extend phase by phase.

## High-Level Architecture

```
Frontend (React + TS + Vite)
        ↓  REST/JSON
Backend API (Flask)
        ↓
Services (Journey, Scoring, Rerouting, AI, Booking, ...)
        ↓
Database (SQLite)          External APIs (Google Maps, OpenAI)
```

- The **frontend** collects input and presents decisions.
- The **backend** orchestrates services and exposes a REST API.
- The **decision engine** computes the numeric score and ranking.
- **Google Maps** supplies route/mapping data.
- **OpenAI** explains and personalizes the decision.
- **SQLite** persists users, routes, journeys, bookings, notifications.

Full detail: [`ARCHITECTURE.md`](./ARCHITECTURE.md).

## Scope of Phase 0

This phase creates **only** the folder structure and documentation. No
application features are implemented. Implementation begins in Phase 1.
