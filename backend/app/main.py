"""FastAPI app — the orchestration brain (requirements §4).

Wires routers, runs DB init + the background job poller on startup.
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from . import llm
from .config import settings
from .db import init_db
from .routers import campaigns, leads, sheets
from .services import poller

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    task = asyncio.create_task(poller.run_forever())
    yield
    task.cancel()


app = FastAPI(title="GMaps Buyer-Finder", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaigns.router)
app.include_router(leads.router)
app.include_router(sheets.router)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "llm_configured": llm.is_configured(),
        "llm_model": settings.llm_model or None,
        "sheet_configured": bool(settings.google_sheet_web_app_url),
        "enrichment_threshold": settings.enrichment_score_threshold,
    }


# ---------- Serve the built Vue SPA (no separate nginx container) ----------

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

if STATIC_DIR.is_dir():

    class SPAStaticFiles(StaticFiles):
        async def get_response(self, path: str, scope) -> Response:
            try:
                response = await super().get_response(path, scope)
            except StarletteHTTPException as exc:
                if exc.status_code != 404:
                    raise
                # Vue Router history mode: let the SPA handle unknown paths.
                return await super().get_response("index.html", scope)
            if response.status_code == 404:
                return await super().get_response("index.html", scope)
            return response

    # Mounted last so it only catches requests the API routers above didn't.
    app.mount("/", SPAStaticFiles(directory=STATIC_DIR, html=True), name="spa")
