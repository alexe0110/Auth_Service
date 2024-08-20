"""add_cascade_ondelete

Revision ID: 8ec6195796d9
Revises: 17af30d1a588
Create Date: 2024-07-30 16:41:11.515755

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '8ec6195796d9'
down_revision: str | None = '17af30d1a588'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    # Drop the existing foreign key constraint
    op.drop_constraint('user_roles_role_id_fkey', 'user_roles', type_='foreignkey')

    # Add the new foreign key constraint with ON DELETE CASCADE
    op.create_foreign_key(
        None,
        'user_roles',
        'roles',
        ['role_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Drop the new foreign key constraint
    op.drop_constraint(None, 'user_roles', type_='foreignkey')

    # Add the old foreign key constraint without ON DELETE CASCADE
    op.create_foreign_key(
        'user_roles_role_id_fkey',
        'user_roles',
        'roles',
        ['role_id'],
        ['id']
    )