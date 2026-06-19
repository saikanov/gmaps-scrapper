"""Normalisation + dedup cascade (requirements §8).

Cascade: place_id/cid/data_id -> phone (E.164) -> root domain -> fuzzy name+city.
place_id resolves ~95% of cross-query duplicates exactly. On merge we keep the
richest record (email wins) and append {query, city} to provenance.
"""
from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlparse

import phonenumbers
from rapidfuzz import fuzz

_LEGAL_SUFFIXES = {
    "gmbh", "ag", "kg", "ohg", "ltd", "llc", "inc", "co", "corp", "company",
    "bv", "nv", "sarl", "sa", "srl", "spa", "pte", "pty", "plc", "llp",
    "trading", "import", "export", "group", "holding", "ev", "ug",
}


def normalize_name(name: str) -> str:
    if not name:
        return ""
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    n = n.lower()
    n = re.sub(r"[^a-z0-9\s]", " ", n)
    tokens = [t for t in n.split() if t and t not in _LEGAL_SUFFIXES]
    return " ".join(tokens).strip()


def normalize_phone(phone: str, region: str | None = None) -> str:
    if not phone:
        return ""
    try:
        parsed = phonenumbers.parse(phone, region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass
    digits = re.sub(r"[^\d+]", "", phone)
    return digits


def root_domain(website: str) -> str:
    if not website:
        return ""
    url = website if "://" in website else f"http://{website}"
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def dedup_key(*, place_id: str, cid: str, phone_e164: str, domain: str, norm_name: str, city: str) -> str:
    """Canonical key for fast index lookup; place_id wins when present."""
    if place_id:
        return f"pid:{place_id}"
    if cid:
        return f"cid:{cid}"
    if phone_e164:
        return f"tel:{phone_e164}"
    if domain:
        return f"dom:{domain}"
    return f"nm:{norm_name}|{normalize_name(city)}"


def fuzzy_name_match(a_norm: str, b_norm: str, threshold: int = 88) -> bool:
    if not a_norm or not b_norm:
        return False
    return fuzz.token_sort_ratio(a_norm, b_norm) >= threshold
