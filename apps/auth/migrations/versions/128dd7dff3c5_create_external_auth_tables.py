"""create external auth tables

Revision ID: 128dd7dff3c5
Revises: 4e30e4a8fe40
Create Date: 2024-08-17 22:36:39.656315

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '128dd7dff3c5'
down_revision: str | None = '4e30e4a8fe40'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    external_auth_provider_table = op.create_table(
        "external_auth_provider",
        sa.Column(
            "id", sa.UUID, primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("name", sa.String, nullable=False)
    )

    op.create_table(
        "user_auth_external",
        sa.Column(
            "id", sa.UUID, primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("user_account_id", sa.UUID, sa.ForeignKey("user_account.id"), nullable=False),
        sa.Column("external_user_id", sa.String, nullable=False, unique=True),
        sa.Column("external_provider_id", sa.UUID, sa.ForeignKey("external_auth_provider.id"), nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("timezone('utc', now())")),
    )

    op.execute(external_auth_provider_table.insert().values(id="d1164a3a-b4bb-44ff-b6bb-0b6d022052aa", name="yandex"))


def downgrade() -> None:
    pass
