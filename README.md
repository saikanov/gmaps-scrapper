# GMaps Buyer-Finder

Internal tool for a commodity-export business: find candidate **buyers**
(importers, distributors, wholesalers, manufacturers) on Google Maps,
semi-automatically.

Flow: `Campaign → AI keyword-gen (per city, local language) → user approve →
scrape (gosom) → dedup → AI scoring → Lead Board → export to Google Sheet`.

See [`requirements.md`](./requirements.md) for the full product/technical spec
(the source of truth).

## Architecture

```
Vue 3 SPA  ──/api/──▶  FastAPI brain  ──▶  gosom/google-maps-scraper (engine)
(frontend)             (backend)      ──▶  Postgres (campaign/job/lead)
                                      ──▶  vLLM (keyword-gen + scoring + enrichment)
                                      ──▶  Apps Script (Google Sheet export)
```

- **backend/** — FastAPI orchestrator. Models, dedup cascade, ingest, the two AI
  touchpoints, a background poller that ingests finished scrape jobs.
- **frontend/** — Vue 3 + Vite + TS + Pinia + Vue Router + Tailwind + PrimeVue.
- **gosom** — pure scraping engine, never modified.
- **google_apps_script.js** — Sheet web app (batch insert, per-campaign tab).

## Run (Docker)

The external network `web` must exist once:

```bash
docker network create web   # if not already present
```

Set secrets in `.env` (see `.env.example`): `LLM_HOST`, `LLM_MODEL`,
`LLM_API_KEY`, `GOOGLE_SHEET_WEB_APP_URL`. Then:

```bash
docker compose up --build
```

- Frontend: served by the `frontend` container on the `web` network (port 80).
- Backend API: `gmaps-backend:8000`, proxied at `/api/` by the frontend nginx.
- Postgres: `gmaps-postgres:5432` (volume `pgdata`).

## LLM note (vLLM / qwen)

The model is a reasoning model. We disable thinking per request via
`chat_template_kwargs: {enable_thinking: false}` plus the gateway header
`x-bf-passthrough-extra-params: true` (see `backend/app/llm.py`). With thinking
on, the endpoint intermittently returns empty completions. Do **not** use the
`/no_think` prompt token on this gateway — it returns empty 100% of the time.

## API surface

| Method · Path | Purpose |
|---|---|
| `POST /api/campaigns` | Create campaign |
| `GET /api/campaigns` | List campaigns + stats |
| `POST /api/campaigns/{id}/keywords` | AI keyword-gen (returns plan) |
| `POST /api/campaigns/{id}/dispatch` | Approved queries → gosom jobs |
| `GET /api/campaigns/{id}/jobs` | Job status (live progress) |
| `POST /api/campaigns/{id}/score` | Batch scoring (+ optional enrichment) |
| `GET /api/campaigns/{id}/leads` | Filtered leads |
| `PATCH /api/leads/{id}` | Update outreach status |
| `POST /api/campaigns/{id}/export` | Export to Google Sheet |
| `POST /api/sheets/add` | Back-compat Apps Script passthrough |

## Dev (without Docker)

Backend:
```bash
cd backend && python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
# point DATABASE_URL at a local Postgres, set LLM_* in env
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend && npm install && npm run dev   # proxies /api → localhost:8000
```
