"""Campaign lifecycle: create, list, keyword-gen, dispatch, jobs, score, export."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import get_db
from ..models import Campaign, Job, Lead
from ..schemas import (
    CampaignCreate,
    CampaignStats,
    DispatchRequest,
    ExportRequest,
    JobOut,
    KeywordPlan,
    MessageOut,
    ScoreRequest,
)
from ..services import enrichment, exporter, geocode, gosom, keyword_gen, scoring

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


async def _get_campaign(db: AsyncSession, campaign_id: uuid.UUID) -> Campaign:
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    return campaign


@router.post("", response_model=CampaignStats)
async def create_campaign(body: CampaignCreate, db: AsyncSession = Depends(get_db)):
    campaign = Campaign(
        commodity=body.commodity.strip(),
        country=body.country.strip(),
        buyer_profile=",".join(body.buyer_profile),
        keyword_mode=body.keyword_mode if body.keyword_mode in ("tiering", "all_at_once") else "tiering",
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return await _stats_for(db, campaign)


async def _stats_for(db: AsyncSession, campaign: Campaign) -> CampaignStats:
    lead_count = await db.scalar(
        select(func.count(Lead.id)).where(Lead.campaign_id == campaign.id)
    )
    rows = (
        await db.execute(
            select(Job.status, func.count(Job.id)).where(Job.campaign_id == campaign.id).group_by(Job.status)
        )
    ).all()
    by_status = {s: c for s, c in rows}
    running = sum(by_status.get(s, 0) for s in ("pending", "dispatched", "running"))
    done = sum(by_status.get(s, 0) for s in ("ingested", "completed"))
    out = CampaignStats.model_validate(campaign, from_attributes=True)
    out.lead_count = lead_count or 0
    out.job_count = sum(by_status.values())
    out.jobs_running = running
    out.jobs_done = done
    out.has_keywords = bool(campaign.keyword_plan)
    return out


@router.get("", response_model=list[CampaignStats])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    campaigns = (
        await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    ).scalars().all()
    return [await _stats_for(db, c) for c in campaigns]


@router.get("/{campaign_id}", response_model=CampaignStats)
async def get_campaign(campaign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    campaign = await _get_campaign(db, campaign_id)
    return await _stats_for(db, campaign)


# ---------- Keyword generation (AI #1) ----------


@router.post("/{campaign_id}/keywords", response_model=KeywordPlan)
async def generate_keywords(campaign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    campaign = await _get_campaign(db, campaign_id)
    plan = await keyword_gen.generate(campaign)
    campaign.keyword_plan = plan.model_dump()
    await db.commit()
    return plan


@router.get("/{campaign_id}/keywords", response_model=KeywordPlan)
async def get_keywords(campaign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    campaign = await _get_campaign(db, campaign_id)
    if not campaign.keyword_plan:
        raise HTTPException(404, "No keyword plan yet — generate first")
    return KeywordPlan.model_validate(campaign.keyword_plan)


# ---------- Dispatch to gosom ----------


@router.post("/{campaign_id}/dispatch", response_model=MessageOut)
async def dispatch(campaign_id: uuid.UUID, body: DispatchRequest, db: AsyncSession = Depends(get_db)):
    campaign = await _get_campaign(db, campaign_id)
    if not body.queries:
        raise HTTPException(400, "No queries to dispatch")

    default_lang = "en"
    if campaign.keyword_plan:
        default_lang = campaign.keyword_plan.get("language", "en")

    dispatched = 0
    errors = 0
    for q in body.queries:
        job = Job(
            campaign_id=campaign.id,
            query=q.query.strip(),
            city=q.city.strip(),
            tier=q.tier,
            lang=q.lang or default_lang,
            status="pending",
        )
        db.add(job)
        await db.flush()  # get job.id
        try:
            # gosom needs a map center; geocode the city, fall back to country.
            coords = await geocode.geocode(job.city) if job.city else None
            if coords is None:
                coords = await geocode.geocode(campaign.country)
            lat, lon = coords or (settings.scrape_fallback_lat, settings.scrape_fallback_lon)
            gosom_id = await gosom.create_job(
                name=f"{campaign.commodity[:30]} · {q.query[:40]}",
                query=q.query,
                lang=job.lang,
                lat=lat,
                lon=lon,
            )
            job.gosom_job_id = gosom_id
            job.status = "dispatched"
            from datetime import datetime, timezone

            job.dispatched_at = datetime.now(timezone.utc)
            dispatched += 1
        except Exception as exc:
            job.status = "error"
            job.error = str(exc)[:500]
            errors += 1

    await db.commit()
    return MessageOut(
        status="ok",
        count=dispatched,
        detail=f"{dispatched} dispatched, {errors} failed. Poller will ingest results.",
    )


@router.get("/{campaign_id}/jobs", response_model=list[JobOut])
async def list_jobs(campaign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await _get_campaign(db, campaign_id)
    jobs = (
        await db.execute(
            select(Job).where(Job.campaign_id == campaign_id).order_by(Job.tier, Job.created_at)
        )
    ).scalars().all()
    return jobs


# ---------- Scoring + enrichment (AI #2) ----------


@router.post("/{campaign_id}/score", response_model=MessageOut)
async def score(campaign_id: uuid.UUID, body: ScoreRequest, db: AsyncSession = Depends(get_db)):
    campaign = await _get_campaign(db, campaign_id)
    stmt = select(Lead).where(Lead.campaign_id == campaign_id)
    if body.only_unscored:
        stmt = stmt.where(Lead.score.is_(None))
    leads = (await db.execute(stmt)).scalars().all()
    scored = await scoring.score_campaign(db, campaign, list(leads))
    enriched = 0
    if body.enrich:
        hi = (
            await db.execute(
                select(Lead).where(
                    Lead.campaign_id == campaign_id,
                    Lead.score >= settings.enrichment_score_threshold,
                    Lead.enriched.is_(False),
                )
            )
        ).scalars().all()
        enriched = await enrichment.enrich_campaign(db, campaign, list(hi))
    await db.commit()
    return MessageOut(status="ok", count=scored, detail=f"scored {scored}, enriched {enriched}")


# ---------- Export ----------


@router.post("/{campaign_id}/export", response_model=MessageOut)
async def export_campaign(campaign_id: uuid.UUID, body: ExportRequest, db: AsyncSession = Depends(get_db)):
    campaign = await _get_campaign(db, campaign_id)
    stmt = select(Lead).where(Lead.campaign_id == campaign_id)
    if body.lead_ids:
        stmt = stmt.where(Lead.id.in_(body.lead_ids))
    else:
        if body.score_gte is not None:
            stmt = stmt.where(Lead.score >= body.score_gte)
        if body.lead_type:
            stmt = stmt.where(Lead.lead_type == body.lead_type)
        if body.city:
            stmt = stmt.where(Lead.city == body.city)
        if body.status:
            stmt = stmt.where(Lead.outreach_status == body.status)
        if body.has_email:
            stmt = stmt.where(Lead.email != "")
    leads = (await db.execute(stmt.order_by(Lead.score.desc().nullslast()))).scalars().all()
    try:
        count = await exporter.export(campaign, list(leads), body.sheet_name)
    except Exception as exc:
        raise HTTPException(502, f"Export failed: {exc}")
    return MessageOut(status="ok", count=count, detail=f"Exported {count} leads")
