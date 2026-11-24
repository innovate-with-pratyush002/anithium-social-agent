"""Add encrypted social account connections."""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d91a6b3f2e10"
down_revision: str | None = "c4e7a19b2d60"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "social_accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("external_account_id", sa.String(length=255), nullable=False),
        sa.Column("account_name", sa.String(length=255), nullable=True),
        sa.Column("account_type", sa.String(length=40), nullable=True),
        sa.Column("access_token_encrypted", sa.String(length=4096), nullable=False),
        sa.Column("refresh_token_encrypted", sa.String(length=4096), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("granted_scopes", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("connected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform", "external_account_id", name="uq_social_account_platform_external_id"),
    )
    op.create_index("ix_social_accounts_user_id", "social_accounts", ["user_id"])
    op.create_index("ix_social_accounts_platform", "social_accounts", ["platform"])


def downgrade() -> None:
    op.drop_index("ix_social_accounts_platform", table_name="social_accounts")
    op.drop_index("ix_social_accounts_user_id", table_name="social_accounts")
    op.drop_table("social_accounts")
