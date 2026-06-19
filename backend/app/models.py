"""ORM models — Campaign / Job / Lead (requirements §6).

One LEAD table for all campaigns, separated by campaign_id (locked §2.5).
Dedup primary key is place_id with a cascade fallback stored in dedup_key (§8).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    commodity: Mapped[str] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(120))
    # buyer_profile stored as comma list of enum values: importer,distributor,...
    buyer_profile: Mapped[str] = mapped_column(String(300), default="")
    keyword_mode: Mapped[str] = mapped_column(String(20), default="tiering")  # tiering | all_at_once
    # AI keyword-gen output cached here so the review screen can re-render.
    keyword_plan: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, server_default=func.now()
    )

    jobs: Mapped[list["Job"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    leads: Mapped[list["Lead"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    # gosom job id (the engine's own uuid), filled after dispatch.
    gosom_job_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    query: Mapped[str] = mapped_column(String(400))
    city: Mapped[str] = mapped_column(String(160), default="")
    tier: Mapped[int] = mapped_column(Integer, default=1)
    lang: Mapped[str] = mapped_column(String(12), default="en")
    # local lifecycle: pending -> dispatched -> running -> completed -> ingested -> error
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    leads_found: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, server_default=func.now()
    )

    campaign: Mapped["Campaign"] = relationship(back_populates="jobs")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=_uuid)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    first_job_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)

    name: Mapped[str] = mapped_column(String(400), default="")
    category: Mapped[str] = mapped_column(String(200), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    city: Mapped[str] = mapped_column(String(160), default="", index=True)
    phone: Mapped[str] = mapped_column(String(60), default="")
    email: Mapped[str] = mapped_column(String(400), default="")
    website: Mapped[str] = mapped_column(String(400), default="")
    gmaps_url: Mapped[str] = mapped_column(Text, default="")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    place_id: Mapped[str] = mapped_column(String(120), default="", index=True)
    cid: Mapped[str] = mapped_column(String(120), default="")

    review_count: Mapped[int] = mapped_column(Integer, default=0)
    review_rating: Mapped[float | None] = mapped_column(Float, nullable=True)

    # AI scoring (§9)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    lead_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # importer|distributor|...
    score_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Enrichment (§9 phase 3)
    enrichment: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    enriched: Mapped[bool] = mapped_column(default=False)

    outreach_status: Mapped[str] = mapped_column(String(20), default="new")  # §6 enum

    dedup_key: Mapped[str] = mapped_column(String(200), default="", index=True)
    # provenance = list of {query, city} that found this lead (prominence signal)
    provenance: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, server_default=func.now()
    )

    campaign: Mapped["Campaign"] = relationship(back_populates="leads")
