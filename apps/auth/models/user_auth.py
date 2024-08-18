import enum
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.postgres import Base


class ExternalAuthProviderEnum(enum.Enum):
    YANDEX = "d1164a3a-b4bb-44ff-b6bb-0b6d022052aa"


class UserAuth(Base):
    __tablename__ = "user_auth"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
    )
    user_account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(nullable=False, server_default=sa.text("true"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=sa.text("timezone('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=sa.text("timezone('utc', now())"))

    account: Mapped["UserAccount"] = relationship(back_populates="internal_auth_data")  # type: ignore # noqa: F821


class ExternalAuthProvider(Base):
    __tablename__ = "external_auth_provider"
    id: Mapped[UUID] = mapped_column(
        primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(nullable=False)


class UserAuthExternal(Base):
    __tablename__ = "user_auth_external"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
    )
    user_account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False)
    external_user_id: Mapped[str] = mapped_column(nullable=False)
    external_provider_id: Mapped[UUID] = mapped_column(sa.ForeignKey("external_auth_provider.id"), nullable=False)
    active: Mapped[bool] = mapped_column(nullable=False, server_default=sa.text("true"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=sa.text("timezone('utc', now())"))

    account: Mapped["UserAccount"] = relationship(back_populates="external_auth_data")  # type: ignore # noqa: F821
