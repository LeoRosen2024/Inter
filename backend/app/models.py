from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import BigInteger, Column, DateTime, Float, JSON, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(UTC)


def new_id() -> str:
    return str(uuid4())


json_type = JSON().with_variant(JSONB, "postgresql")


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_type=DateTime(timezone=True),
        nullable=False,
    )


class SocialProfile(TimestampMixin, table=True):
    __tablename__ = "social_profiles"
    __table_args__ = (UniqueConstraint("platform", "handle", name="uq_social_profile_platform_handle"),)

    id: str = Field(default_factory=new_id, primary_key=True, max_length=36)
    platform: str = Field(default="instagram", max_length=32, index=True)
    role: str = Field(default="competitor", max_length=32, index=True)
    handle: str = Field(max_length=128, index=True)
    display_name: str = Field(max_length=160)
    profile_url: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=1000)
    followers_count: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    total_views_count: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    engagement_rate: float = Field(default=0, sa_column=Column(Float, nullable=False))
    is_active: bool = Field(default=True, index=True)
    raw_payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(json_type, nullable=False))


class Reel(TimestampMixin, table=True):
    __tablename__ = "reels"
    __table_args__ = (UniqueConstraint("profile_id", "external_id", name="uq_reel_profile_external"),)

    id: str = Field(default_factory=new_id, primary_key=True, max_length=36)
    profile_id: str | None = Field(default=None, foreign_key="social_profiles.id", index=True)
    external_id: str = Field(max_length=255, index=True)
    scope: str = Field(default="trending", max_length=32, index=True)
    title: str = Field(max_length=255, index=True)
    description: str = Field(default="", sa_column=Column(Text, nullable=False))
    status: str = Field(default="online", max_length=32, index=True)
    source_handle: str = Field(default="", max_length=128, index=True)
    source_url: str | None = Field(default=None, max_length=1000)
    media_url: str | None = Field(default=None, max_length=1000)
    thumbnail_url: str | None = Field(default=None, max_length=1000)
    duration_seconds: int = Field(default=0, ge=0)
    views_count: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    likes_count: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    comments_count: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    trend_score: float = Field(default=0, sa_column=Column(Float, nullable=False))
    growth_percent: float = Field(default=0, sa_column=Column(Float, nullable=False))
    published_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    version: int = Field(default=1, ge=1)
    raw_payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(json_type, nullable=False))


class ReelScript(TimestampMixin, table=True):
    __tablename__ = "reel_scripts"
    __table_args__ = (UniqueConstraint("reel_id", name="uq_reel_script_reel"),)

    id: str = Field(default_factory=new_id, primary_key=True, max_length=36)
    reel_id: str = Field(foreign_key="reels.id", index=True)
    hook: str = Field(default="", sa_column=Column(Text, nullable=False))
    body: str = Field(default="", sa_column=Column(Text, nullable=False))
    call_to_action: str = Field(default="", sa_column=Column(Text, nullable=False))
    status: str = Field(default="draft", max_length=32, index=True)
    version: int = Field(default=1, ge=1)


class ReelMetricSnapshot(SQLModel, table=True):
    __tablename__ = "reel_metric_snapshots"
    __table_args__ = (UniqueConstraint("reel_id", "observed_at", name="uq_metric_reel_observed"),)

    id: str = Field(default_factory=new_id, primary_key=True, max_length=36)
    reel_id: str = Field(foreign_key="reels.id", index=True)
    observed_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )
    views_count: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    likes_count: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    comments_count: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))


class Tag(TimestampMixin, table=True):
    __tablename__ = "tags"

    id: str = Field(default_factory=new_id, primary_key=True, max_length=36)
    name: str = Field(max_length=80, unique=True, index=True)


class ReelTag(SQLModel, table=True):
    __tablename__ = "reel_tags"
    __table_args__ = (UniqueConstraint("reel_id", "tag_id", name="uq_reel_tag"),)

    id: str = Field(default_factory=new_id, primary_key=True, max_length=36)
    reel_id: str = Field(foreign_key="reels.id", index=True)
    tag_id: str = Field(foreign_key="tags.id", index=True)


class MediaAsset(TimestampMixin, table=True):
    __tablename__ = "media_assets"

    id: str = Field(default_factory=new_id, primary_key=True, max_length=36)
    reel_id: str | None = Field(default=None, foreign_key="reels.id", index=True)
    kind: str = Field(max_length=32, index=True)
    storage_key: str = Field(max_length=500, unique=True)
    public_url: str | None = Field(default=None, max_length=1000)
    content_type: str | None = Field(default=None, max_length=128)
    size_bytes: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    checksum_sha256: str | None = Field(default=None, max_length=64)


class SyncJob(TimestampMixin, table=True):
    __tablename__ = "sync_jobs"

    id: str = Field(default_factory=new_id, primary_key=True, max_length=36)
    provider: str = Field(default="apify", max_length=32, index=True)
    actor_id: str = Field(max_length=255)
    run_id: str | None = Field(default=None, max_length=255, unique=True, index=True)
    dataset_id: str | None = Field(default=None, max_length=255)
    source_url: str = Field(max_length=1000)
    requested_limit: int = Field(default=20, ge=1, le=100)
    status: str = Field(default="queued", max_length=32, index=True)
    result_count: int = Field(default=0, ge=0)
    error_message: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    input_payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(json_type, nullable=False))
    started_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    finished_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))


class AppSetting(SQLModel, table=True):
    __tablename__ = "app_settings"

    id: str = Field(default="default", primary_key=True, max_length=36)
    display_name: str = Field(default="Leo Rosen", max_length=160)
    email: str = Field(default="", max_length=320)
    locale: str = Field(default="de", max_length=10)
    trend_notifications: bool = Field(default=True)
    autosave: bool = Field(default=True)
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
