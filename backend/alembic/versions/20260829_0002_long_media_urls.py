"""Allow long Instagram media URLs."""

from alembic import op
import sqlalchemy as sa


revision = "20260829_0002"
down_revision = "20260829_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for column in ("source_url", "media_url", "thumbnail_url"):
        op.alter_column("reels", column, existing_type=sa.VARCHAR(length=1000), type_=sa.Text())


def downgrade() -> None:
    for column in ("source_url", "media_url", "thumbnail_url"):
        op.alter_column("reels", column, existing_type=sa.Text(), type_=sa.VARCHAR(length=1000))
