"""AI lead scoring — touchpoint #2 (requirements §9).

Cheap, high-volume batch scoring. Input is the already prefiltered+deduped lead
set. Output per lead: lead_type (enum §6), score 0-100, one-sentence reason.
Never run before prefilter+dedup.
"""
from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from .. import llm
from ..config import settings
from ..models import Campaign, Lead

LEAD_TYPES = {"importer", "distributor", "wholesaler", "manufacturer", "retailer", "irrelevant"}

SYSTEM = """You score Google-Maps business leads for a commodity EXPORT business
that is looking for BUYERS (importers, distributors, wholesalers, manufacturers
that consume the commodity, HORECA).

For EACH lead return:
- "id": echo the lead id given
- "lead_type": one of importer | distributor | wholesaler | manufacturer | retailer | irrelevant
- "score": integer 0-100 (priority for outreach)
- "score_reason": ONE short sentence (the deciding factor)

Scoring rubric (heaviest first):
- category & name match the target buyer type (most important)
- has website / email (+)
- B2B / wholesale / import signals in the name (+)
- looks like small retail / end-consumer (−)
- clearly unrelated business -> low score + lead_type "irrelevant"

Respond with ONLY JSON: {"leads": [ {"id": "...", "lead_type": "...", "score": 0, "score_reason": "..."} ]}"""


def _lead_brief(lead: Lead) -> dict:
    return {
        "id": str(lead.id),
        "name": lead.name,
        "category": lead.category,
        "has_website": bool(lead.website),
        "has_email": bool(lead.email),
        "review_count": lead.review_count,
        "city": lead.city,
    }


async def _score_batch(campaign: Campaign, leads: list[Lead]) -> None:
    context = (
        f"Commodity: {campaign.commodity}\n"
        f"Target country: {campaign.country}\n"
        f"Buyer profile: {campaign.buyer_profile or 'any B2B buyer'}\n\n"
        "Leads:\n" + json.dumps([_lead_brief(l) for l in leads], ensure_ascii=False)
    )
    raw = await llm.chat_json(SYSTEM, context, temperature=0.1, max_tokens=8000)
    items = raw.get("leads", raw) if isinstance(raw, dict) else raw
    by_id = {str(l.id): l for l in leads}
    for item in items or []:
        lead = by_id.get(str(item.get("id")))
        if not lead:
            continue
        lt = str(item.get("lead_type", "")).lower().strip()
        lead.lead_type = lt if lt in LEAD_TYPES else "irrelevant"
        try:
            lead.score = max(0, min(100, int(item.get("score", 0))))
        except (TypeError, ValueError):
            lead.score = 0
        lead.score_reason = str(item.get("score_reason", ""))[:500]


async def score_campaign(db: AsyncSession, campaign: Campaign, leads: list[Lead]) -> int:
    """Score the given leads in batches. Returns number scored."""
    if not llm.is_configured() or not leads:
        return 0
    scored = 0
    batch = settings.scoring_batch_size
    for i in range(0, len(leads), batch):
        chunk = leads[i : i + batch]
        try:
            await _score_batch(campaign, chunk)
            scored += len(chunk)
            await db.flush()
        except Exception:
            # don't let one bad batch abort the whole run
            continue
    return scored
