"""Back-compat Sheet passthrough (requirements §11, §13).

Forwards JSON as-is to the Apps Script web app so the legacy /api/sheets/add
contract keeps working.
"""
from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, Request

from ..config import settings

router = APIRouter(prefix="/api/sheets", tags=["sheets"])


@router.post("/add")
async def add_to_sheet(request: Request):
    if not settings.google_sheet_web_app_url:
        raise HTTPException(500, "Google Sheets Web App URL not configured")
    payload = await request.json()
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
        resp = await client.post(settings.google_sheet_web_app_url, json=payload)
        if resp.status_code >= 400:
            raise HTTPException(502, f"Apps Script responded {resp.status_code}")
    return {"status": "success"}
