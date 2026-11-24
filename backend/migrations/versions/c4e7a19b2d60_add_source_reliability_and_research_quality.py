"""add source reliability and research quality

Revision ID: c4e7a19b2d60
Revises: 8d2a6f41c9b3
Create Date: 2026-11-24
"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "c4e7a19b2d60"
down_revision: str | None = "8d2a6f41c9b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "sources",
        sa.Column("reliability_score", sa.Float(), nullable=False, server_default="0.7"),
    )
    op.add_column("research_items", sa.Column("quality_score", sa.Float(), nullable=True))
    op.add_column(
        "research_items",
        sa.Column(
            "quality_signals",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("research_items", "quality_signals")
    op.drop_column("research_items", "quality_score")
    op.drop_column("sources", "reliability_score")
