"""Add optional transcript text to reels."""

from alembic import op
import sqlalchemy as sa

revision = "20260829_0003"
down_revision = "20260829_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("reels", sa.Column("transcript", sa.Text(), nullable=False, server_default=""))
    op.alter_column("reels", "transcript", server_default=None)


def downgrade() -> None:
    op.drop_column("reels", "transcript")
