from functools import lru_cache
from uuid import UUID

from db.postgres import AsyncSession
from repositories.account import UserAccountRepository
from schemas.user_account import (
    ChangeCredentialsIn,
    LoginUserIn,
    RegisterUserIn,
    UserAccountLoginHistorySchema,
    UserAccountSchema,
)
from schemas.user_roles import UserRole

from .dependencies import PostgresUserAccountRepository


class UserAccountService:
    def __init__(self, account_repository: UserAccountRepository) -> None:
        self.account_repository = account_repository

    async def register(self, session: AsyncSession, data: RegisterUserIn, user_agent: str) -> UserAccountSchema:
        account = await self.account_repository.create_account(session=session, data=data)
        await self.account_repository.create_login_history(session=session, account=account, user_agent=user_agent)

        return UserAccountSchema(
            id=account.id,
            email=account.internal_auth_data.email,
            last_name=account.last_name,
            first_name=account.first_name,
            middle_name=account.middle_name,
            gender=account.gender,
            birthdate=account.birthdate,
            roles=account.roles,
        )

    async def login(self, session: AsyncSession, data: LoginUserIn, user_agent: str) -> UserAccountSchema:
        auth_data = await self.account_repository.verify_credentials(session=session, data=data)
        await self.account_repository.create_login_history(
            session=session, account=auth_data.account, user_agent=user_agent
        )

        return UserAccountSchema(
            id=auth_data.account.id,
            email=auth_data.email,
            last_name=auth_data.account.last_name,
            first_name=auth_data.account.first_name,
            middle_name=auth_data.account.middle_name,
            gender=auth_data.account.gender,
            birthdate=auth_data.account.birthdate,
            roles=auth_data.account.roles,
        )

    async def get_by_id(self, session: AsyncSession, account_id: str):
        account = await self.account_repository.get_by_id(session=session, account_id=account_id)

        return UserAccountSchema(
            id=account.id,
            email=account.internal_auth_data.email,
            last_name=account.last_name,
            first_name=account.first_name,
            middle_name=account.middle_name,
            gender=account.gender,
            birthdate=account.birthdate,
            roles=account.roles,
        )

    async def change_credentials(
        self, session: AsyncSession, account_id: str, data: ChangeCredentialsIn
    ) -> UserAccountSchema:
        account = await self.account_repository.change_credentials(
            session=session, account_id=account_id, email=data.email, password=data.password
        )

        return UserAccountSchema(
            id=account.id,
            email=account.internal_auth_data.email,
            last_name=account.last_name,
            first_name=account.first_name,
            middle_name=account.middle_name,
            gender=account.gender,
            birthdate=account.birthdate,
            roles=account.roles,
        )

    async def assign_user_role(self, session: AsyncSession, role_ids: list[UUID], account_id: UUID) -> list[UserRole]:
        await self.account_repository.role_assigment(session, role_ids, account_id)
        return await self.account_repository.get_user_roles(session, account_id)

    async def unassign_user_role(self, session: AsyncSession, account_id: UUID, role_id: UUID) -> list[UserRole]:
        await self.account_repository.role_unassigment(session, account_id, role_id)
        return await self.account_repository.get_user_roles(session, account_id)

    async def get_user_roles(self, session: AsyncSession, user_id: UUID) -> list[UserRole]:
        return await self.account_repository.get_user_roles(session, user_id)

    async def check_user_role(self, session: AsyncSession, account_id: UUID, role_id: UUID) -> bool:
        roles = await self.account_repository.get_user_roles(session, account_id)

        return any(role.role_id == role_id for role in roles)

    async def get_login_history(self, session: AsyncSession, account_id: str, page_number: int, page_size: int):
        login_history = await self.account_repository.get_login_history(
            session=session, account_id=account_id, limit=page_size, offset=(page_number - 1) * page_size
        )

        return [
            UserAccountLoginHistorySchema(id=item.id, user_agent=item.user_agent, login_time=item.login_time)
            for item in login_history
        ]


@lru_cache(maxsize=1)
def get_account_service(
    account_repository: PostgresUserAccountRepository,
):
    return UserAccountService(account_repository=account_repository)
