"""add email to account table

Revision ID: 1b78a733f014
Revises: 128dd7dff3c5
Create Date: 2024-08-17 23:14:33.970710

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '1b78a733f014'
down_revision: str | None = '128dd7dff3c5'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("user_account", sa.Column("email", sa.String(), nullable=False, unique=True))


def downgrade() -> None:
    op.drop_column("user_account", "email")
