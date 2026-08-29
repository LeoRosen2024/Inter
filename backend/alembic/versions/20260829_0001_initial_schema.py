"""Create the initial Inter Reels schema.

Revision ID: 20260829_0001
Revises:
Create Date: 2026-08-29
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260829_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "social_profiles",
        *timestamp_columns(),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("handle", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("profile_url", sa.String(length=500), nullable=True),
        sa.Column("avatar_url", sa.String(length=1000), nullable=True),
        sa.Column("followers_count", sa.BigInteger(), nullable=False),
        sa.Column("total_views_count", sa.BigInteger(), nullable=False),
        sa.Column("engagement_rate", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform", "handle", name="uq_social_profile_platform_handle"),
    )
    op.create_index("ix_social_profiles_handle", "social_profiles", ["handle"])
    op.create_index("ix_social_profiles_is_active", "social_profiles", ["is_active"])
    op.create_index("ix_social_profiles_platform", "social_profiles", ["platform"])
    op.create_index("ix_social_profiles_role", "social_profiles", ["role"])

    op.create_table(
        "reels",
        *timestamp_columns(),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("profile_id", sa.String(length=36), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source_handle", sa.String(length=128), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("media_url", sa.String(length=1000), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=1000), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("views_count", sa.BigInteger(), nullable=False),
        sa.Column("likes_count", sa.BigInteger(), nullable=False),
        sa.Column("comments_count", sa.BigInteger(), nullable=False),
        sa.Column("trend_score", sa.Float(), nullable=False),
        sa.Column("growth_percent", sa.Float(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["social_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", "external_id", name="uq_reel_profile_external"),
    )
    for column in ("external_id", "profile_id", "scope", "source_handle", "status", "title"):
        op.create_index(f"ix_reels_{column}", "reels", [column])

    op.create_table(
        "reel_scripts",
        *timestamp_columns(),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("reel_id", sa.String(length=36), nullable=False),
        sa.Column("hook", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("call_to_action", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["reel_id"], ["reels.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reel_id", name="uq_reel_script_reel"),
    )
    op.create_index("ix_reel_scripts_reel_id", "reel_scripts", ["reel_id"])
    op.create_index("ix_reel_scripts_status", "reel_scripts", ["status"])

    op.create_table(
        "reel_metric_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("reel_id", sa.String(length=36), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("views_count", sa.BigInteger(), nullable=False),
        sa.Column("likes_count", sa.BigInteger(), nullable=False),
        sa.Column("comments_count", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["reel_id"], ["reels.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reel_id", "observed_at", name="uq_metric_reel_observed"),
    )
    op.create_index("ix_reel_metric_snapshots_observed_at", "reel_metric_snapshots", ["observed_at"])
    op.create_index("ix_reel_metric_snapshots_reel_id", "reel_metric_snapshots", ["reel_id"])

    op.create_table(
        "tags",
        *timestamp_columns(),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_tags_name", "tags", ["name"], unique=True)

    op.create_table(
        "reel_tags",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("reel_id", sa.String(length=36), nullable=False),
        sa.Column("tag_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["reel_id"], ["reels.id"]),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reel_id", "tag_id", name="uq_reel_tag"),
    )
    op.create_index("ix_reel_tags_reel_id", "reel_tags", ["reel_id"])
    op.create_index("ix_reel_tags_tag_id", "reel_tags", ["tag_id"])

    op.create_table(
        "media_assets",
        *timestamp_columns(),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("reel_id", sa.String(length=36), nullable=True),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("public_url", sa.String(length=1000), nullable=True),
        sa.Column("content_type", sa.String(length=128), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["reel_id"], ["reels.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index("ix_media_assets_kind", "media_assets", ["kind"])
    op.create_index("ix_media_assets_reel_id", "media_assets", ["reel_id"])

    op.create_table(
        "sync_jobs",
        *timestamp_columns(),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("actor_id", sa.String(length=255), nullable=False),
        sa.Column("run_id", sa.String(length=255), nullable=True),
        sa.Column("dataset_id", sa.String(length=255), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("requested_limit", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id"),
    )
    op.create_index("ix_sync_jobs_provider", "sync_jobs", ["provider"])
    op.create_index("ix_sync_jobs_run_id", "sync_jobs", ["run_id"], unique=True)
    op.create_index("ix_sync_jobs_status", "sync_jobs", ["status"])

    op.create_table(
        "app_settings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("locale", sa.String(length=10), nullable=False),
        sa.Column("trend_notifications", sa.Boolean(), nullable=False),
        sa.Column("autosave", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
    op.drop_index("ix_sync_jobs_status", table_name="sync_jobs")
    op.drop_index("ix_sync_jobs_run_id", table_name="sync_jobs")
    op.drop_index("ix_sync_jobs_provider", table_name="sync_jobs")
    op.drop_table("sync_jobs")
    op.drop_index("ix_media_assets_reel_id", table_name="media_assets")
    op.drop_index("ix_media_assets_kind", table_name="media_assets")
    op.drop_table("media_assets")
    op.drop_index("ix_reel_tags_tag_id", table_name="reel_tags")
    op.drop_index("ix_reel_tags_reel_id", table_name="reel_tags")
    op.drop_table("reel_tags")
    op.drop_index("ix_tags_name", table_name="tags")
    op.drop_table("tags")
    op.drop_index("ix_reel_metric_snapshots_reel_id", table_name="reel_metric_snapshots")
    op.drop_index("ix_reel_metric_snapshots_observed_at", table_name="reel_metric_snapshots")
    op.drop_table("reel_metric_snapshots")
    op.drop_index("ix_reel_scripts_status", table_name="reel_scripts")
    op.drop_index("ix_reel_scripts_reel_id", table_name="reel_scripts")
    op.drop_table("reel_scripts")
    for column in ("title", "status", "source_handle", "scope", "profile_id", "external_id"):
        op.drop_index(f"ix_reels_{column}", table_name="reels")
    op.drop_table("reels")
    op.drop_index("ix_social_profiles_role", table_name="social_profiles")
    op.drop_index("ix_social_profiles_platform", table_name="social_profiles")
    op.drop_index("ix_social_profiles_is_active", table_name="social_profiles")
    op.drop_index("ix_social_profiles_handle", table_name="social_profiles")
    op.drop_table("social_profiles")
