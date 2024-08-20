"""create tables

Revision ID: c5ffb8117669
Revises:
Create Date: 2024-07-21 22:33:02.696195

"""

from typing import Sequence  # noqa: UP035

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5ffb8117669"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_account",
        sa.Column(
            "id", sa.UUID, primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("first_name", sa.String, nullable=False),
        sa.Column("last_name", sa.String, nullable=False),
        sa.Column("middle_name", sa.String, nullable=True),
        sa.Column("gender", sa.String, nullable=False),
        sa.Column("birthdate", sa.Date, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("timezone('utc', now())")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("timezone('utc', now())")),
    )

    op.create_table(
        "user_auth",
        sa.Column(
            "id", sa.UUID, primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("user_account_id", sa.UUID, sa.ForeignKey("user_account.id"), nullable=False),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("timezone('utc', now())")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("timezone('utc', now())")),
        sa.UniqueConstraint("user_account_id", "email", "active"),
    )

    op.create_table(
        "user_login_history",
        sa.Column(
            "id", sa.UUID, primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("user_account_id", sa.UUID, sa.ForeignKey("user_account.id"), nullable=False),
        sa.Column("user_agent", sa.String, nullable=False),
        sa.Column("login_time", sa.DateTime, nullable=False, server_default=sa.text("timezone('utc', now())")),
    )

    roles_table = op.create_table(
        "roles",
        sa.Column(
            "id", sa.UUID, primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("name", sa.String, nullable=False, unique=True),
    )

    op.create_table(
        "user_roles",
        sa.Column(
            "id", sa.UUID, primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("user_account_id", sa.UUID, sa.ForeignKey("user_account.id"), nullable=False),
        sa.Column("role_id", sa.UUID, sa.ForeignKey("roles.id"), nullable=False),
        sa.UniqueConstraint("user_account_id", "role_id"),
    )

    op.execute(roles_table.insert().values(id="853a5a98-4dc4-4fc5-a95d-9a17c8ef7635", name="ADMIN"))


def downgrade() -> None:
    op.drop_table("user_roles")
    op.drop_table("roles")
    op.drop_table("user_login_history")
    op.drop_table("user_auth")
    op.drop_table("user_account")
