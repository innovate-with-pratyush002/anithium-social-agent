"""add research intelligence tracking

Revision ID: 8d2a6f41c9b3
Revises: 3fc7dcd987d7
Create Date: 2026-11-23
"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "8d2a6f41c9b3"
down_revision: str | None = "3fc7dcd987d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "research_items",
        sa.Column("analysis_status", sa.String(length=20), nullable=False, server_default="pending"),
    )
    op.add_column(
        "research_items",
        sa.Column("analysis_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("research_items", sa.Column("analysis_error", sa.Text(), nullable=True))
    op.add_column(
        "research_items",
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_research_items_analysis_status", "research_items", ["analysis_status"], unique=False
    )
    op.create_index(
        "ix_research_items_topic_discovered",
        "research_items",
        ["topic", "discovered_at"],
        unique=False,
    )
    op.execute(
        "UPDATE research_items SET analysis_status = 'completed', "
        "analyzed_at = updated_at WHERE relevance_score IS NOT NULL "
        "AND metadata_json ? 'intelligence'"
    )


def downgrade() -> None:
    op.drop_index("ix_research_items_topic_discovered", table_name="research_items")
    op.drop_index("ix_research_items_analysis_status", table_name="research_items")
    op.drop_column("research_items", "analyzed_at")
    op.drop_column("research_items", "analysis_error")
    op.drop_column("research_items", "analysis_attempts")
    op.drop_column("research_items", "analysis_status")
