"""Pydantic request/response schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# ---------- Campaign ----------


class CampaignCreate(BaseModel):
    commodity: str
    country: str
    buyer_profile: list[str] = Field(default_factory=list)  # importer, distributor, ...
    keyword_mode: str = "tiering"  # tiering | all_at_once


class CampaignOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    commodity: str
    country: str
    buyer_profile: str
    keyword_mode: str
    created_at: datetime


class CampaignStats(CampaignOut):
    lead_count: int = 0
    job_count: int = 0
    jobs_running: int = 0
    jobs_done: int = 0
    has_keywords: bool = False


# ---------- Keyword generation (§7) ----------


class CityOut(BaseModel):
    name: str
    tier: int = 1
    reason: str = ""


class QueryOut(BaseModel):
    query: str
    city: str = ""
    tier: int = 1


class KeywordPlan(BaseModel):
    language: str = "en"
    buyer_terms: list[str] = Field(default_factory=list)
    commodity_terms: list[str] = Field(default_factory=list)
    cities: list[CityOut] = Field(default_factory=list)
    queries: list[QueryOut] = Field(default_factory=list)


# ---------- Dispatch ----------


class DispatchQuery(BaseModel):
    query: str
    city: str = ""
    tier: int = 1
    lang: str | None = None


class DispatchRequest(BaseModel):
    queries: list[DispatchQuery]


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    query: str
    city: str
    tier: int
    lang: str
    status: str
    leads_found: int
    error: str | None = None
    dispatched_at: datetime | None = None
    created_at: datetime


# ---------- Lead ----------


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    campaign_id: uuid.UUID
    name: str
    category: str
    address: str
    city: str
    phone: str
    email: str
    website: str
    gmaps_url: str
    latitude: float | None = None
    longitude: float | None = None
    place_id: str
    review_count: int
    review_rating: float | None = None
    score: int | None = None
    lead_type: str | None = None
    score_reason: str | None = None
    enrichment: dict | None = None
    enriched: bool = False
    outreach_status: str
    provenance: list | None = None
    created_at: datetime


class LeadUpdate(BaseModel):
    outreach_status: str | None = None


class ScoreRequest(BaseModel):
    # if true, also enrich leads scoring >= threshold (phase 3)
    enrich: bool = False
    only_unscored: bool = True


class ExportRequest(BaseModel):
    sheet_name: str | None = None
    score_gte: int | None = None
    lead_type: str | None = None
    city: str | None = None
    status: str | None = None
    has_email: bool | None = None
    lead_ids: list[uuid.UUID] | None = None  # explicit selection overrides filters


class MessageOut(BaseModel):
    status: str = "ok"
    detail: str | None = None
    count: int | None = None
