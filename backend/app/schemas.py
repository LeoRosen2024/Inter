from datetime import datetime
from typing import Any

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel


class ApiModel(SQLModel):
    model_config = ConfigDict(from_attributes=True)


class ReelCreate(ApiModel):
    profile_id: str | None = None
    external_id: str = Field(min_length=1, max_length=255)
    scope: str = "mine"
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    status: str = Field(default="draft", max_length=32)
    source_handle: str = Field(default="", max_length=128)
    source_url: str | None = None
    media_url: str | None = None
    thumbnail_url: str | None = None
    duration_seconds: int = Field(default=0, ge=0)
    views_count: int = Field(default=0, ge=0)
    likes_count: int = Field(default=0, ge=0)
    comments_count: int = Field(default=0, ge=0)
    trend_score: float = Field(default=0, ge=0, le=100)
    growth_percent: float = 0

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, value: str) -> str:
        if value not in {"trending", "mine"}:
            raise ValueError("scope must be 'trending' or 'mine'")
        return value


class ReelUpdate(ApiModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = Field(default=None, max_length=32)
    source_url: str | None = None
    media_url: str | None = None
    thumbnail_url: str | None = None
    duration_seconds: int | None = Field(default=None, ge=0)
    version: int | None = Field(default=None, ge=1)


class ReelSummary(ApiModel):
    id: str
    title: str
    source_handle: str
    scope: str
    status: str
    thumbnail_url: str | None
    duration_seconds: int
    views_count: int
    likes_count: int
    comments_count: int
    trend_score: float
    growth_percent: float
    published_at: datetime | None
    updated_at: datetime
    version: int


class ReelScriptPublic(ApiModel):
    id: str
    reel_id: str
    hook: str
    body: str
    call_to_action: str
    status: str
    version: int
    updated_at: datetime


class ReelScriptUpdate(ApiModel):
    hook: str | None = None
    body: str | None = None
    call_to_action: str | None = None
    status: str | None = Field(default=None, max_length=32)
    version: int | None = Field(default=None, ge=1)


class ReelDetail(ReelSummary):
    description: str
    transcript: str
    source_url: str | None
    media_url: str | None
    tags: list[str] = Field(default_factory=list)
    script: ReelScriptPublic | None = None


class ReelList(ApiModel):
    items: list[ReelSummary]
    total: int
    limit: int
    offset: int


class CompetitorCreate(ApiModel):
    handle: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=160)
    platform: str = Field(default="instagram", max_length=32)
    profile_url: str | None = None
    avatar_url: str | None = None
    followers_count: int = Field(default=0, ge=0)
    total_views_count: int = Field(default=0, ge=0)
    engagement_rate: float = Field(default=0, ge=0)


class CompetitorPublic(ApiModel):
    id: str
    platform: str
    handle: str
    display_name: str
    profile_url: str | None
    avatar_url: str | None
    followers_count: int
    total_views_count: int
    engagement_rate: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CompetitorList(ApiModel):
    items: list[CompetitorPublic]
    total: int
    limit: int
    offset: int


class AppSettingPublic(ApiModel):
    id: str
    display_name: str
    email: str
    locale: str
    trend_notifications: bool
    autosave: bool
    updated_at: datetime


class AppSettingUpdate(ApiModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=160)
    email: str | None = Field(default=None, max_length=320)
    locale: str | None = Field(default=None, max_length=10)
    trend_notifications: bool | None = None
    autosave: bool | None = None


class ImportCreate(ApiModel):
    source_url: str = Field(min_length=8, max_length=1000)
    limit: int = Field(default=20, ge=1, le=20)
    actor_input: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized.startswith(("https://", "http://")):
            raise ValueError("source_url must use http or https")
        return normalized


class ImportPublic(ApiModel):
    id: str
    provider: str
    actor_id: str
    run_id: str | None
    dataset_id: str | None
    source_url: str
    requested_limit: int
    status: str
    result_count: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class ApifyConfiguration(ApiModel):
    configured: bool
    actor_id: str | None


class HealthResponse(ApiModel):
    status: str
    database: str | None = None
