"""Thin client for the gosom/google-maps-scraper engine (never rewritten — §2.3).

We talk to its HTTP API to create jobs and poll status, and read the CSV it
writes per job from the shared data folder.
"""
from __future__ import annotations

import csv
import os

import httpx

from ..config import settings

# gosom statuses we treat as terminal-success / terminal-failure
DONE = {"completed", "finished", "ok"}
FAILED = {"error", "failed", "cancelled"}


async def create_job(*, name: str, query: str, lang: str, lat: float, lon: float) -> str:
    """Create a single-keyword job in gosom, return its job id.

    gosom requires a map center (lat/lon); callers geocode the city/country.
    """
    body = {
        "name": name,
        "keywords": [query],
        "lang": lang or settings.scrape_lang_default,
        "zoom": settings.scrape_zoom,
        "depth": settings.scrape_depth,
        "max_time": settings.scrape_max_time,
        "fast_mode": settings.scrape_fast_mode,
        "email": settings.scrape_email,
        "lat": str(lat),
        "lon": str(lon),
        "radius": settings.scrape_radius,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{settings.gosom_url}/api/v1/jobs", json=body)
        resp.raise_for_status()
        data = resp.json()
    # gosom returns the created job; id key may be "id".
    job_id = data.get("id") or data.get("job", {}).get("id")
    if not job_id:
        raise RuntimeError(f"gosom did not return a job id: {data}")
    return str(job_id)


async def job_status(gosom_job_id: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{settings.gosom_url}/api/v1/jobs/{gosom_job_id}")
        resp.raise_for_status()
        data = resp.json()
    # gosom returns the field capitalised ("Status"); accept both just in case.
    status = (data.get("Status") or data.get("status") or data.get("state") or "").lower()
    return status


def csv_path(gosom_job_id: str) -> str:
    return os.path.join(settings.gmaps_data_dir, f"{gosom_job_id}.csv")


def read_rows(gosom_job_id: str) -> list[dict]:
    """Read the per-job CSV gosom produced. Returns [] if not present yet."""
    path = csv_path(gosom_job_id)
    if not os.path.exists(path):
        return []
    rows: list[dict] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows
