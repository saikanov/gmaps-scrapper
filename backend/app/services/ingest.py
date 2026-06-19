"""Ingest gosom CSV rows into LEAD: field map (§10) -> free prefilter (§9) ->
dedup cascade (§8) -> insert/merge.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Job, Lead
from . import dedup

# Categories that are almost never a commodity buyer (free prefilter signal).
_IRRELEVANT_HINTS = (
    "atm", "parking", "gas station", "hotel", "hostel", "pharmacy", "dentist",
    "doctor", "hospital", "school", "university", "church", "mosque", "temple",
    "gym", "salon", "spa", "barber", "tourist", "museum", "park", "bank branch",
)


def _first_email(emails: str) -> str:
    if not emails:
        return ""
    # gosom may emit a list-like string; take first plausible address.
    for part in emails.replace(";", ",").split(","):
        part = part.strip().strip("[]'\" ")
        if "@" in part:
            return part
    return ""


def _to_float(v: str) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _to_int(v: str) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def map_row(row: dict) -> dict:
    """gosom CSV row -> LEAD field dict (requirements §10)."""
    address = row.get("complete_address") or row.get("address") or ""
    return {
        "name": (row.get("title") or "").strip(),
        "category": (row.get("category") or "").strip(),
        "address": address.strip(),
        "phone": (row.get("phone") or "").strip(),
        "email": _first_email(row.get("emails") or ""),
        "website": (row.get("website") or "").strip(),
        "gmaps_url": (row.get("link") or "").strip(),
        "latitude": _to_float(row.get("latitude")),
        "longitude": _to_float(row.get("longitude")),
        "place_id": (row.get("place_id") or "").strip(),
        "cid": (row.get("cid") or row.get("data_id") or "").strip(),
        "review_count": _to_int(row.get("review_count")),
        "review_rating": _to_float(row.get("review_rating")),
    }


def prefilter(fields: dict) -> bool:
    """Free heuristic prefilter — return True to KEEP the lead."""
    if not fields["name"]:
        return False
    # must have at least one contact channel
    if not (fields["phone"] or fields["website"] or fields["email"]):
        return False
    cat = (fields["category"] or "").lower()
    if any(h in cat for h in _IRRELEVANT_HINTS):
        return False
    return True


class _Indexes:
    """In-memory dedup index over a campaign's existing leads."""

    def __init__(self, leads: list[Lead]):
        self.by_place: dict[str, Lead] = {}
        self.by_phone: dict[str, Lead] = {}
        self.by_domain: dict[str, Lead] = {}
        self.fuzzy: list[tuple[str, str, Lead]] = []  # (norm_name, norm_city, lead)
        for lead in leads:
            self._register(lead)

    def _register(self, lead: Lead) -> None:
        if lead.place_id:
            self.by_place[lead.place_id] = lead
        if lead.cid:
            self.by_place.setdefault(f"cid:{lead.cid}", lead)
        phone = dedup.normalize_phone(lead.phone)
        if phone:
            self.by_phone.setdefault(phone, lead)
        dom = dedup.root_domain(lead.website)
        if dom:
            self.by_domain.setdefault(dom, lead)
        self.fuzzy.append((dedup.normalize_name(lead.name), dedup.normalize_name(lead.city), lead))

    def find(self, fields: dict, phone_e164: str, domain: str) -> Lead | None:
        if fields["place_id"] and fields["place_id"] in self.by_place:
            return self.by_place[fields["place_id"]]
        if fields["cid"] and f"cid:{fields['cid']}" in self.by_place:
            return self.by_place[f"cid:{fields['cid']}"]
        if phone_e164 and phone_e164 in self.by_phone:
            return self.by_phone[phone_e164]
        if domain and domain in self.by_domain:
            return self.by_domain[domain]
        nn = dedup.normalize_name(fields["name"])
        nc = dedup.normalize_name(fields["city"])
        for o_name, o_city, lead in self.fuzzy:
            if nc and o_city and nc == o_city and dedup.fuzzy_name_match(nn, o_name):
                return lead
        return None

    def add(self, lead: Lead) -> None:
        self._register(lead)


def _merge(existing: Lead, fields: dict, prov: dict) -> None:
    """Keep richest record: fill blanks, prefer having email; add provenance."""
    for key in ("phone", "website", "email", "address", "category", "place_id", "cid", "gmaps_url"):
        if not getattr(existing, key) and fields.get(key):
            setattr(existing, key, fields[key])
    if fields.get("review_count", 0) > (existing.review_count or 0):
        existing.review_count = fields["review_count"]
        existing.review_rating = fields.get("review_rating")
    prov_list = list(existing.provenance or [])
    if prov not in prov_list:
        prov_list.append(prov)
        existing.provenance = prov_list


async def ingest_job(db: AsyncSession, job: Job, rows: list[dict]) -> int:
    """Process all rows of one finished gosom job. Returns # new leads inserted."""
    existing = (
        await db.execute(select(Lead).where(Lead.campaign_id == job.campaign_id))
    ).scalars().all()
    idx = _Indexes(list(existing))

    prov = {"query": job.query, "city": job.city}
    inserted = 0

    for row in rows:
        fields = map_row(row)
        if not prefilter(fields):
            continue
        # city comes from the job (gosom rows have no clean city column).
        fields["city"] = job.city
        phone_e164 = dedup.normalize_phone(fields["phone"])
        domain = dedup.root_domain(fields["website"])

        match = idx.find(fields, phone_e164, domain)
        if match is not None:
            _merge(match, fields, prov)
            continue

        lead = Lead(
            campaign_id=job.campaign_id,
            first_job_id=job.id,
            provenance=[prov],
            **fields,
        )
        lead.dedup_key = dedup.dedup_key(
            place_id=fields["place_id"],
            cid=fields["cid"],
            phone_e164=phone_e164,
            domain=domain,
            norm_name=dedup.normalize_name(fields["name"]),
            city=job.city,
        )
        db.add(lead)
        idx.add(lead)
        inserted += 1

    await db.flush()
    return inserted
