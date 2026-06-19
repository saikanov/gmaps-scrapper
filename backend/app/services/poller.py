"""Background job poller — the orchestration heartbeat.

Periodically checks gosom for jobs we've dispatched. When a job finishes we pull
its CSV, ingest+dedup it, and (optionally) auto-score the campaign's new leads.
Runs as a single asyncio task started on app startup.
"""
from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from ..config import settings
from ..db import SessionLocal
from ..models import Job
from . import gosom, ingest

log = logging.getLogger("poller")

_ACTIVE = {"pending", "dispatched", "running"}


async def _tick() -> None:
    async with SessionLocal() as db:
        jobs = (
            await db.execute(select(Job).where(Job.status.in_(_ACTIVE), Job.gosom_job_id.isnot(None)))
        ).scalars().all()

        for job in jobs:
            try:
                status = await gosom.job_status(job.gosom_job_id)  # type: ignore[arg-type]
            except Exception as exc:  # gosom unreachable / transient
                log.warning("status check failed for job %s: %s", job.id, exc)
                continue

            if status in gosom.FAILED:
                job.status = "error"
                job.error = f"gosom status={status}"
            elif status in gosom.DONE:
                rows = gosom.read_rows(job.gosom_job_id)  # type: ignore[arg-type]
                try:
                    inserted = await ingest.ingest_job(db, job, rows)
                    job.leads_found = inserted
                    job.status = "ingested"
                except Exception as exc:
                    log.exception("ingest failed for job %s", job.id)
                    job.status = "error"
                    job.error = str(exc)[:500]
            elif status:
                job.status = "running"

        await db.commit()


async def run_forever() -> None:
    log.info("job poller started (interval=%ss)", settings.poll_interval_seconds)
    while True:
        try:
            await _tick()
        except Exception:
            log.exception("poller tick failed")
        await asyncio.sleep(settings.poll_interval_seconds)
