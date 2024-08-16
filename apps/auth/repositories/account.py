import abc
from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

import bcrypt
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from db.postgres import AsyncSession
from models import Role, Roles, UserAccount, UserAuth, UserLoginHistory, UserRoles
from models.exceptions import (
    InvalidCredentialsError,
    RoleNotExistError,
    UserAlreadyExistError,
    UserNotExistsError,
    UserNotRegisteredError,
    UserRoleAlreadyExistError,
    UserRoleNotExistError,
)
from schemas.user_account import LoginUserIn, RegisterUserIn


class UserAccountRepository(abc.ABC):
    @abc.abstractmethod
    async def create_account(self, session: AsyncSession, data: RegisterUserIn) -> UserAccount:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_login_history(self, session: AsyncSession, account: UserAccount, user_agent: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def verify_credentials(self, session: AsyncSession, data: LoginUserIn) -> UserAuth:
        raise NotImplementedError

    @abc.abstractmethod
    async def change_credentials(
        self, session: AsyncSession, account_id: str, email: str | None, password: str | None
    ) -> UserAccount:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, session: AsyncSession, account_id: str) -> UserAccount:
        raise NotImplementedError

    @abc.abstractmethod
    async def role_assigment(self, session: AsyncSession, role_ids: list[UUID], account_id: UUID):
        raise NotImplementedError

    @abc.abstractmethod
    async def role_unassigment(self, session: AsyncSession, role_id: UUID, account_id: UUID):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_roles(self, session: AsyncSession, account_id: UUID):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_login_history(
        self, session: AsyncSession, account_id: str, limit: int, offset: int
    ) -> Sequence[UserLoginHistory]:
        raise NotImplementedError


class PostgresUserAccountRepository(UserAccountRepository):
    def _hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode()

    async def create_account(self, session: AsyncSession, data: RegisterUserIn) -> UserAccount:
        hashed_password = self._hash_password(data.password)
        account_roles = await session.scalars(sa.select(Roles).where(Roles.id == Role.PORTAL_USER.value))

        account = UserAccount(
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
            gender=data.gender,
            birthdate=data.birthdate,
            internal_auth_data=UserAuth(email=data.email, password=hashed_password),
            roles=account_roles.all(),
        )
        try:
            session.add(account)
            await session.flush()
        except IntegrityError as e:
            raise UserAlreadyExistError from e
        return account

    async def create_login_history(self, session: AsyncSession, account: UserAccount, user_agent: str):
        login_history = UserLoginHistory(user_agent=user_agent, account=account)
        session.add(login_history)
        await session.flush()

    async def verify_credentials(self, session: AsyncSession, data: LoginUserIn):
        auth_data = await session.scalar(
            sa.select(UserAuth)
            .where(UserAuth.email == data.email)
            .options(
                joinedload(UserAuth.account).joinedload(UserAccount.roles),
            )
        )
        if not auth_data:
            raise InvalidCredentialsError

        if not bcrypt.checkpw(data.password.encode(), auth_data.password.encode()):
            raise InvalidCredentialsError

        return auth_data

    async def change_credentials(self, session: AsyncSession, account_id: str, email: str | None, password: str | None):
        account = await session.get_one(
            UserAccount,
            ident=account_id,
            options=(joinedload(UserAccount.internal_auth_data), joinedload(UserAccount.roles)),
        )

        if password:
            account.internal_auth_data.password = self._hash_password(password)
        if email:
            account.internal_auth_data.email = email

        account.internal_auth_data.updated_at = datetime.utcnow()

        try:
            await session.flush()
        except IntegrityError as e:
            raise UserAlreadyExistError from e
        return account

    async def get_by_id(self, session: AsyncSession, account_id: str) -> UserAccount:
        user_account = await session.scalar(
            sa.select(UserAccount)
            .where(UserAccount.id == account_id)
            .options(joinedload(UserAccount.internal_auth_data), joinedload(UserAccount.roles))
        )

        if not user_account:
            raise UserNotExistsError

        return user_account

    async def role_assigment(self, session: AsyncSession, role_ids: list[UUID], account_id: UUID) -> None:
        data_all = []

        for role_id in role_ids:
            stmt = (
                sa.select(UserRoles).where(UserRoles.role_id == role_id).where(UserRoles.user_account_id == account_id)
            )
            user_role = await session.scalar(stmt)

            data = UserRoles(role_id=role_id, user_account_id=account_id)

            if not await session.get(Roles, role_id):
                raise RoleNotExistError

            if not await session.get(UserAccount, account_id):
                raise UserNotRegisteredError

            if user_role:
                raise UserRoleAlreadyExistError

            data_all.append(data)

        session.add_all(data_all)
        await session.flush()

    async def role_unassigment(self, session: AsyncSession, account_id: UUID, role_id: UUID) -> None:
        stmt = sa.select(UserRoles).where(UserRoles.role_id == role_id).where(UserRoles.user_account_id == account_id)
        user_role = await session.scalar(stmt)

        if not user_role:
            raise UserRoleNotExistError

        await session.delete(user_role)
        await session.flush()

    async def get_user_roles(self, session: AsyncSession, account_id: UUID):
        stmt = sa.select(UserRoles).where(UserRoles.user_account_id == account_id)
        user_role = await session.scalars(stmt)

        return user_role.fetchall()

    async def get_login_history(
        self, session: AsyncSession, account_id: str, limit: int, offset: int
    ) -> Sequence[UserLoginHistory]:
        res = await session.scalars(
            sa.select(UserLoginHistory)
            .where(UserLoginHistory.user_account_id == account_id)
            .order_by(UserLoginHistory.login_time.desc())
            .offset(offset)
            .limit(limit)
        )
        return res.fetchall()
