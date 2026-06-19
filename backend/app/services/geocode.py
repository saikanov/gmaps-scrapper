"""Tiny geocoder so we can give gosom a map center (it requires lat/lon).

Uses OpenStreetMap Nominatim (no API key). Results are cached in-process and
keyed by place string — tiering reuses the same cities across many buyer terms,
so the cache keeps us well under Nominatim's ~1 req/s fair-use limit.
"""
from __future__ import annotations

import asyncio

import httpx

_NOMINATIM = "https://nominatim.openstreetmap.org/search"
_cache: dict[str, tuple[float, float] | None] = {}
_lock = asyncio.Lock()


async def geocode(place: str) -> tuple[float, float] | None:
    """Return (lat, lon) for a place name, or None if it can't be resolved."""
    key = place.strip().lower()
    if not key:
        return None
    if key in _cache:
        return _cache[key]
    async with _lock:
        if key in _cache:  # filled while we waited for the lock
            return _cache[key]
        result: tuple[float, float] | None = None
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    _NOMINATIM,
                    params={"q": place, "format": "json", "limit": 1},
                    headers={"User-Agent": "gmaps-scrapper/1.0"},
                )
                resp.raise_for_status()
                data = resp.json()
            if data:
                result = (float(data[0]["lat"]), float(data[0]["lon"]))
        except Exception:
            result = None
        _cache[key] = result
        return result
