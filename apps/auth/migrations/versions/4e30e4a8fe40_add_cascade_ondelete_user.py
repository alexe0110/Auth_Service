"""add_cascade_ondelete_user

Revision ID: 4e30e4a8fe40
Revises: 8ec6195796d9
Create Date: 2024-08-02 11:21:37.761022

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4e30e4a8fe40'
down_revision: str | None = '8ec6195796d9'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    # Drop the existing foreign key constraint
    op.drop_constraint('user_auth_user_account_id_fkey', 'user_auth', type_='foreignkey')
    op.drop_constraint('user_login_history_user_account_id_fkey', 'user_login_history', type_='foreignkey')
    op.drop_constraint('user_roles_user_account_id_fkey', 'user_roles', type_='foreignkey')

    # Add the new foreign key constraint with ON DELETE CASCADE
    op.create_foreign_key(
        None,
        'user_auth',
        'user_account',
        ['user_account_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        None,
        'user_login_history',
        'user_account',
        ['user_account_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        None,
        'user_roles',
        'user_account',
        ['user_account_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Drop the new foreign key constraint
    op.drop_constraint(None, 'user_auth', type_='foreignkey')
    op.drop_constraint(None, 'user_login_history', type_='foreignkey')

    # Add the old foreign key constraint without ON DELETE CASCADE
    op.create_foreign_key(
        'user_auth_user_account_id_fkey',
        'user_auth',
        'user_account',
        ['user_account_id'],
        ['id'],
    )
    op.create_foreign_key(
        'user_login_history_user_account_id_fkey',
        'user_login_history',
        'user_account',
        ['user_account_id'],
        ['id'],
    )

    op.create_foreign_key(
        'user_roles_user_account_id_fkey',
        'user_roles',
        'user_account',
        ['user_account_id'],
        ['id'],
    )