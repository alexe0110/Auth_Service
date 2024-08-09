from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.postgres import Base


class UserLoginHistory(Base):
    __tablename__ = "user_login_history"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, nullable=False, unique=True, server_default=sa.text("gen_random_uuid()")
    )
    user_account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False)
    user_agent: Mapped[str] = mapped_column(nullable=False)
    login_time: Mapped[datetime] = mapped_column(nullable=False, server_default=sa.text("timezone('utc', now())"))

    account: Mapped["UserAccount"] = relationship(back_populates="login_history")  # type: ignore # noqa: F821
