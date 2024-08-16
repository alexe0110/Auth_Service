from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from db.postgres import Base


class UserRoles(Base):
    __tablename__ = "user_roles"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
    )
    user_account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[UUID] = mapped_column(sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
