"""AI keyword generator — touchpoint #1 (requirements §7).

Cross-product {commodity variants} x {buyer types} x {trade-hub cities}, all in
the target country's business language, cities ranked by import trade-hub rather
than population. Output matches the `emit_keywords` schema.
"""
from __future__ import annotations

import itertools

from .. import llm
from ..models import Campaign
from ..schemas import KeywordPlan

SYSTEM = """You are a B2B trade-lead research assistant for a commodity EXPORT business.
The user exports a commodity and wants to find BUYERS (importers, distributors,
wholesalers, manufacturers that consume the commodity, HORECA) in a target country
via Google Maps.

Your job: produce Google Maps search queries that maximise relevant buyer coverage.

Rules:
- Write ALL buyer terms, commodity terms and queries in the OFFICIAL BUSINESS
  LANGUAGE of the target country (Germany -> German, UAE -> Arabic + English,
  Japan -> Japanese, etc.). Set "language" to the primary ISO code.
- Rank cities by IMPORT TRADE-HUB relevance (seaports / logistics hubs = tier 1),
  NOT by population. Give a short reason per city.
- Match buyer types to the user's buyer profile. If the profile is only
  importer/distributor, DO NOT include retail terms.
- Include local synonyms / product-form variants of the commodity.
- Build the cross-product of {commodity term} x {buyer term} x {city}. Put
  tier-1 (port/hub) queries first.
- Keep total queries reasonable (aim 20-60). Prefer the strongest combinations.

Respond with ONLY a JSON object, no prose, of the exact shape:
{
  "language": "de",
  "buyer_terms": ["Importeur", "Großhändler"],
  "commodity_terms": ["Rohkaffee", "grüner Kaffee"],
  "cities": [{"name": "Hamburg", "tier": 1, "reason": "largest port / coffee hub"}],
  "queries": [{"query": "Rohkaffee Importeur Hamburg", "city": "Hamburg", "tier": 1}]
}"""


def _user_prompt(campaign: Campaign) -> str:
    profile = campaign.buyer_profile or "importer, distributor, wholesaler, manufacturer"
    mode = campaign.keyword_mode
    cap = "Aim for ~24 of the strongest queries (tier-1 heavy)." if mode == "tiering" else \
        "You may produce the full matrix (up to ~60 queries)."
    return (
        f"Commodity: {campaign.commodity}\n"
        f"Target country: {campaign.country}\n"
        f"Buyer profile (allowed types): {profile}\n"
        f"Keyword mode: {mode}\n"
        f"{cap}\n"
        "Generate the keyword plan JSON now."
    )


def _fallback_plan(campaign: Campaign) -> KeywordPlan:
    """Deterministic plan when the LLM is unreachable, so the pipeline still runs."""
    buyer_terms = [t.strip() for t in (campaign.buyer_profile or "importer,distributor,wholesaler").split(",") if t.strip()]
    if not buyer_terms:
        buyer_terms = ["importer", "distributor", "wholesaler"]
    commodity_terms = [campaign.commodity]
    cities = [{"name": campaign.country, "tier": 1, "reason": "country-wide fallback"}]
    queries = [
        {"query": f"{c} {b} {campaign.country}", "city": campaign.country, "tier": 1}
        for c, b in itertools.product(commodity_terms, buyer_terms)
    ]
    return KeywordPlan(
        language="en",
        buyer_terms=buyer_terms,
        commodity_terms=commodity_terms,
        cities=[c for c in cities],  # type: ignore[arg-type]
        queries=queries,  # type: ignore[arg-type]
    )


async def generate(campaign: Campaign) -> KeywordPlan:
    if not llm.is_configured():
        return _fallback_plan(campaign)
    try:
        raw = await llm.chat_json(SYSTEM, _user_prompt(campaign), temperature=0.3, max_tokens=8000)
        plan = KeywordPlan.model_validate(raw)
        if not plan.queries:
            return _fallback_plan(campaign)
        # ensure each query carries a tier (tier-1 default) and trim blanks
        plan.queries = [q for q in plan.queries if q.query.strip()]
        return plan
    except Exception:
        return _fallback_plan(campaign)
