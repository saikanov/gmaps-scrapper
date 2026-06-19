"""Selective enrichment — expensive, only for high-score leads (requirements §9).

Fetch the lead's website, summarise "what they sell/need", try to find a real
(non-generic) email, and optionally revise the score.
"""
from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

from .. import llm
from ..config import settings
from ..models import Campaign, Lead

_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_GENERIC_PREFIX = ("info", "contact", "office", "hello", "mail", "admin", "sales", "support")

SYSTEM = """You analyse a B2B company's website text for a commodity export business.
Return ONLY JSON:
{
  "summary": "1-2 sentences: what they sell or buy",
  "is_buyer": true/false,           // could they import/buy the commodity?
  "best_email": "real contact email or empty",
  "revised_score": 0-100            // your adjusted priority score
}"""


async def _fetch_text(website: str) -> tuple[str, list[str]]:
    url = website if "://" in website else f"https://{website}"
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 (lead-research)"})
        resp.raise_for_status()
        html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.get_text(" ").split())[:6000]
    emails = list(dict.fromkeys(_EMAIL_RE.findall(html)))
    return text, emails


def _pick_real_email(emails: list[str], llm_email: str) -> str:
    if llm_email and "@" in llm_email:
        return llm_email
    non_generic = [e for e in emails if e.split("@")[0].lower() not in _GENERIC_PREFIX]
    return (non_generic or emails or [""])[0]


async def enrich_lead(campaign: Campaign, lead: Lead) -> None:
    if not lead.website:
        return
    try:
        text, emails = await _fetch_text(lead.website)
    except Exception as exc:
        lead.enrichment = {"error": f"fetch failed: {exc}"[:300]}
        lead.enriched = True
        return

    result: dict = {"page_emails": emails[:5]}
    if llm.is_configured() and text:
        try:
            ctx = (
                f"Commodity: {campaign.commodity}\nCountry: {campaign.country}\n"
                f"Company: {lead.name}\n\nWebsite text:\n{text}"
            )
            raw = await llm.chat_json(SYSTEM, ctx, temperature=0.2, max_tokens=1024)
            result.update(
                {
                    "summary": raw.get("summary", ""),
                    "is_buyer": raw.get("is_buyer"),
                    "best_email": raw.get("best_email", ""),
                }
            )
            if isinstance(raw.get("revised_score"), (int, float)):
                lead.score = max(0, min(100, int(raw["revised_score"])))
        except Exception as exc:
            result["llm_error"] = str(exc)[:200]

    best = _pick_real_email(emails, result.get("best_email", ""))
    if best:
        result["best_email"] = best
        if not lead.email or lead.email.split("@")[0].lower() in _GENERIC_PREFIX:
            lead.email = best
    lead.enrichment = result
    lead.enriched = True


async def enrich_campaign(db: AsyncSession, campaign: Campaign, leads: list[Lead]) -> int:
    """Enrich leads scoring >= threshold that aren't enriched yet."""
    if not leads:
        return 0
    count = 0
    for lead in leads:
        if lead.enriched:
            continue
        if (lead.score or 0) < settings.enrichment_score_threshold:
            continue
        await enrich_lead(campaign, lead)
        count += 1
        await db.flush()
    return count
