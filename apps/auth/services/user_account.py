from functools import lru_cache
from uuid import UUID

from db.postgres import AsyncSession
from models.user_auth import ExternalAuthProviderEnum
from repositories.account import UserAccountRepository
from schemas.user_account import (
    ChangeCredentialsIn,
    LoginUserIn,
    LoginUserViaExternalProviderSchema,
    RegisterUserIn,
    UserAccountLoginHistorySchema,
    UserAccountSchema,
)
from schemas.user_roles import UserRole

from .dependencies import PostgresUserAccountRepository, YandexHTTPClient


class UserAccountService:
    def __init__(self, account_repository: UserAccountRepository, yandex_http_client: YandexHTTPClient) -> None:
        self.account_repository = account_repository
        self.yandex_http_client = yandex_http_client

    async def register(self, session: AsyncSession, data: RegisterUserIn, user_agent: str) -> UserAccountSchema:
        account = await self.account_repository.create_account(session=session, data=data)
        await self.account_repository.create_login_history(session=session, account=account, user_agent=user_agent)

        return UserAccountSchema.model_validate(account, from_attributes=True)

    async def login(self, session: AsyncSession, data: LoginUserIn, user_agent: str) -> UserAccountSchema:
        auth_data = await self.account_repository.verify_credentials(session=session, data=data)
        await self.account_repository.create_login_history(
            session=session, account=auth_data.account, user_agent=user_agent
        )

        return UserAccountSchema.model_validate(auth_data.account, from_attributes=True)

    async def get_by_id(self, session: AsyncSession, account_id: str):
        account = await self.account_repository.get_by_id(session=session, account_id=account_id)

        return UserAccountSchema.model_validate(account, from_attributes=True)

    async def change_credentials(
        self, session: AsyncSession, account_id: str, data: ChangeCredentialsIn
    ) -> UserAccountSchema:
        account = await self.account_repository.change_credentials(
            session=session, account_id=account_id, email=data.email, password=data.password
        )

        return UserAccountSchema.model_validate(account, from_attributes=True)

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

    async def login_via_yandex(self, session: AsyncSession, code: str, user_agent: str):
        token_resp = await self.yandex_http_client.get_token(code=code)
        client_info = await self.yandex_http_client.login(token_resp.access_token)

        data = LoginUserViaExternalProviderSchema.model_validate({
            "id": client_info.id,
            "email": client_info.default_email,
            "first_name": client_info.first_name,
            "last_name": client_info.last_name,
            "gender": client_info.sex,
            "birthdate": client_info.birthday,
        })

        account = await self.account_repository.login_via_external_provider(
            session=session,
            provider_id=ExternalAuthProviderEnum.YANDEX.value,
            data=data
        )

        await self.account_repository.create_login_history(
            session=session, account=account, user_agent=user_agent
        )

        return UserAccountSchema.model_validate(account, from_attributes=True)


@lru_cache(maxsize=1)
def get_account_service(
    account_repository: PostgresUserAccountRepository,
    yandex_http_client: YandexHTTPClient
):
    return UserAccountService(account_repository=account_repository, yandex_http_client=yandex_http_client)
