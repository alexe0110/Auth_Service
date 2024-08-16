"""create portal_user role

Revision ID: 17af30d1a588
Revises: c5ffb8117669
Create Date: 2024-07-23 12:28:17.219437

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "17af30d1a588"
down_revision: str | None = "c5ffb8117669"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

roles_table = sa.table(
    "roles",
    sa.column("id", sa.UUID),
    sa.column("name", sa.String),
)

PORTAL_USER_ROLE_ID = "12891149-54d1-4b77-a198-1fad074e0213"


def upgrade() -> None:
    op.execute(roles_table.insert().values(id=PORTAL_USER_ROLE_ID, name="PORTAL_USER"))


def downgrade() -> None:
    op.execute(roles_table.delete().where(roles_table.c.id == PORTAL_USER_ROLE_ID))
