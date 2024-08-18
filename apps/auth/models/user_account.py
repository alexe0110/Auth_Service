from datetime import date, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint, text

from db.postgres import Base


def create_partition(target, connection, **kw) -> None:
    connection.execute(
        text("""CREATE TABLE IF NOT EXISTS "user_account_male" PARTITION OF "user_account" FOR VALUES IN ('male')""")
    )
    connection.execute(
        text("""CREATE TABLE IF NOT EXISTS "user_account_female" PARTITION OF "user_account" FOR VALUES IN ('female')""")
    )


class UserAccount(Base):
    __tablename__ = "user_account"
    __table_args__ = (
        UniqueConstraint('id', 'gender'),
        {
            'postgresql_partition_by': 'LIST (gender)',
            'listeners': [('after_create', create_partition)],
        }
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    middle_name: Mapped[str] = mapped_column(nullable=True)
    gender: Mapped[str] = mapped_column(nullable=False)
    birthdate: Mapped[date] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(nullable=False, server_default=sa.text("true"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=sa.text("timezone('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=sa.text("timezone('utc', now())"))

    internal_auth_data: Mapped["UserAuth"] = relationship(back_populates="account")  # type: ignore # noqa: F821
    external_auth_data: Mapped[list["UserAuthExternal"]] = relationship(back_populates="account")  # type: ignore # noqa: F821
    roles: Mapped[list["Roles"]] = relationship(secondary="user_roles")  # type: ignore # noqa: F821
    login_history: Mapped[list["UserLoginHistory"]] = relationship(back_populates="account")  # type: ignore # noqa: F821
