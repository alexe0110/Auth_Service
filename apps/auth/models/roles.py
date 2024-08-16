from enum import Enum
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from db.postgres import Base


class Role(Enum):
    ADMIN = "853a5a98-4dc4-4fc5-a95d-9a17c8ef7635"
    PORTAL_USER = "12891149-54d1-4b77-a198-1fad074e0213"


class Roles(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
