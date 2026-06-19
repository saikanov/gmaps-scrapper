"""Lead board: filtered listing + outreach status update."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Lead
from ..schemas import LeadOut, LeadUpdate

router = APIRouter(prefix="/api", tags=["leads"])

_OUTREACH = {"new", "contacted", "replied", "qualified", "rejected", "won"}


@router.get("/campaigns/{campaign_id}/leads", response_model=list[LeadOut])
async def list_leads(
    campaign_id: uuid.UUID,
    score_gte: int | None = Query(None),
    type: str | None = Query(None),
    city: str | None = Query(None),
    status: str | None = Query(None),
    has_email: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Lead).where(Lead.campaign_id == campaign_id)
    if score_gte is not None:
        stmt = stmt.where(Lead.score >= score_gte)
    if type:
        stmt = stmt.where(Lead.lead_type == type)
    if city:
        stmt = stmt.where(Lead.city == city)
    if status:
        stmt = stmt.where(Lead.outreach_status == status)
    if has_email:
        stmt = stmt.where(Lead.email != "")
    stmt = stmt.order_by(Lead.score.desc().nullslast(), Lead.review_count.desc())
    leads = (await db.execute(stmt)).scalars().all()
    return leads


@router.patch("/leads/{lead_id}", response_model=LeadOut)
async def update_lead(lead_id: uuid.UUID, body: LeadUpdate, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    if body.outreach_status is not None:
        if body.outreach_status not in _OUTREACH:
            raise HTTPException(400, f"Invalid outreach_status. Allowed: {sorted(_OUTREACH)}")
        lead.outreach_status = body.outreach_status
    await db.commit()
    await db.refresh(lead)
    return lead
