"""Google Sheet exporter (requirements §13).

Build CRM-style rows from leads and POST them (batched) to the Apps Script web
app. 1 campaign = 1 sheet/tab named "(<COUNTRY>) Lead Database" by default.
Re-export to the same sheet appends (Apps Script handles that).
"""
from __future__ import annotations

from datetime import date

import httpx

from ..config import settings
from ..models import Campaign, Lead


def default_sheet_name(campaign: Campaign) -> str:
    return f"({campaign.country}) Lead Database"


def lead_to_row(lead: Lead, campaign: Campaign) -> dict:
    # Apps Script fills: No, Tanggal, Nama Perusahaan, PIC, Jabatan, No Handphone,
    # Email, Negara, Kota, Alamat, Account Executive, Noted. GMaps fills what it can.
    noted_bits = []
    if lead.lead_type:
        noted_bits.append(lead.lead_type)
    if lead.score is not None:
        noted_bits.append(f"score {lead.score}")
    if lead.website:
        noted_bits.append(lead.website)
    return {
        "date": date.today().isoformat(),
        "companyName": lead.name,
        "phone": lead.phone,
        "email": lead.email,
        "country": campaign.country,
        "city": lead.city,
        "address": lead.address,
        "noted": " · ".join(noted_bits),
    }


async def export(campaign: Campaign, leads: list[Lead], sheet_name: str | None = None) -> int:
    if not settings.google_sheet_web_app_url:
        raise RuntimeError("GOOGLE_SHEET_WEB_APP_URL not configured")
    if not leads:
        return 0
    payload = {
        "sheetName": sheet_name or default_sheet_name(campaign),
        "rows": [lead_to_row(l, campaign) for l in leads],
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
        resp = await client.post(settings.google_sheet_web_app_url, json=payload)
        resp.raise_for_status()
    return len(leads)
