This is Claude Memory Across Sessions. Every important thing like architecture changes etc must be recorded here as context for future agents.

## Project: GMaps Buyer-Finder (commodity-export buyer discovery)
Source of truth = `requirements.md`. Build kicked off 2026-06-16: full rewrite of the
old vanilla-JS tool into the target architecture, all 3 phases at once.

### Stack decisions (this build)
- **Backend** = FastAPI "brain" under `backend/app/` (package, run `app.main:app`).
  Async SQLAlchemy 2.0 + **Postgres** (asyncpg). Tables auto-created on startup
  (`init_db`, no Alembic yet). Models use cross-dialect `Uuid` (native UUID on PG,
  works on SQLite too for local testing).
- **LLM** = OpenAI-compatible **vLLM** endpoint (NOT Anthropic). Creds in `.env`:
  `LLM_HOST`, `LLM_MODEL` (vllm/qwen3.5-35b), `LLM_API_KEY`. Client = `app/llm.py`.
- **Frontend** = Vue 3 + Vite + TS + Pinia + Vue Router + Tailwind + PrimeVue, in
  `frontend/`. Old `public/*.html` deprecated (not deleted). Design = "trade/customs
  manifest" identity: harbor-ink + maritime-teal, Space Grotesk / Inter / IBM Plex Mono,
  status chips + mono score badges. Builds clean (`npm run build`, `npm run typecheck`).
- **Postgres + nginx** wired in `docker-compose.yml`; nginx now proxies ALL `/api/`
  → backend (backend talks to gosom itself). gosom engine unchanged (locked §2.3).

### CRITICAL: vLLM qwen "thinking" gotcha (cost me real debugging time)
- The model is a reasoning model. With thinking ON it **intermittently returns empty
  completions** (~40% empty) and is slow.
- The `/no_think` prompt token on this gateway returns empty **100%** of the time — DO NOT USE.
- FIX (works, 5/5, ~1.6s): disable thinking per-request via
  `extra_body={"chat_template_kwargs": {"enable_thinking": false}}` PLUS header
  `extra_headers={"x-bf-passthrough-extra-params": "true"}` (gateway opt-in to pass
  extra params). Implemented in `app/llm.py`. User confirmed this header+param combo.
- llm.py also: strips `<think>…</think>` (incl. unclosed), extracts JSON robustly,
  retries 3x. Keyword-gen verified producing real localized German plans (lang=de,
  trade-hub ports Hamburg/Bremen tier-1).

### Pipeline / AI touchpoints
- AI #1 keyword-gen (`services/keyword_gen.py`): cross-product buyer×commodity×city,
  local language, trade-hub tiering. Has deterministic fallback if LLM down.
- Dedup cascade (`services/dedup.py`, `ingest.py`): place_id → phone(E.164) →
  root-domain → fuzzy name+city. Merge keeps richest record + appends provenance.
- Background **poller** (`services/poller.py`) ingests finished gosom jobs every ~8s.
- AI #2 scoring (`services/scoring.py`, batches) + selective enrichment
  (`services/enrichment.py`, website fetch, only score ≥ threshold=70).

### Deviations from requirements to note
- VeeValidate+Zod and @tanstack/vue-query (listed §12.1) were NOT used — kept deps lean;
  simple manual validation + axios instead. Revisit if forms grow.
- No auth yet (open question §17 unresolved). No Alembic (create_all on startup).

### How it was verified (no Docker in this WSL — user runs compose later)
- Backend imports + dedup/ingest unit logic + full ASGI e2e on SQLite (mock gosom +
  export, real LLM keyword-gen & scoring). Frontend `build` + `typecheck` both green.

---
- [requirements.md](requirements.md) — product/technical source of truth (LOCKED decisions in §2).
