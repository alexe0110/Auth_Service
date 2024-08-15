from datetime import UTC, datetime, timedelta
from functools import lru_cache
from uuid import UUID

import jwt

from core.settings import settings
from models.exceptions import GenerateTokensError
from repositories.token import TokenRepository

from .dependencies import RedisTokenRepository


class TokenService:
    def __init__(self, token_repository: TokenRepository) -> None:
        self.token_repository = token_repository
        self.access_token_lifetime = settings.api.ACCESS_TOKEN_LIFETIME_SEC
        self.refresh_token_lifetime = settings.api.REFRESH_TOKEN_LIFETIME_SEC
        self.secret_key = settings.api.JWT_SECRET_KEY
        self.session_key = "{account_id}::{refresh_token}"

    def generate_access_token(self, payload: dict):
        return jwt.encode(
            {**payload, "exp": datetime.now(tz=UTC) + timedelta(seconds=self.access_token_lifetime)},
            key=self.secret_key,
        )

    def generate_refresh_token(self, payload: dict):
        return jwt.encode(
            {**payload, "exp": datetime.now(tz=UTC) + timedelta(seconds=self.refresh_token_lifetime)},
            key=self.secret_key,
        )

    async def create_session(self, account_id: UUID, access_token_data: dict, refresh_token_data) -> tuple[str, str]:
        try:
            access_token = self.generate_access_token(access_token_data)
            refresh_token = self.generate_refresh_token(refresh_token_data)

            await self.token_repository.setex(
                name=self.session_key.format(account_id=str(account_id), refresh_token=refresh_token),
                time=self.refresh_token_lifetime,
                value=access_token,
            )
        except Exception as e:
            print("\n\n\t ERROR", e)
            raise GenerateTokensError from e

        return access_token, refresh_token

    async def delete_session(self, refresh_token: str):
        decoded_token = self.decode_token(refresh_token)
        await self.token_repository.delete_key(
            name=self.session_key.format(account_id=decoded_token["account_id"], refresh_token=refresh_token)
        )

    def decode_token(self, token: str):
        return jwt.decode(token, key=self.secret_key, algorithms=["HS256"])


@lru_cache(maxsize=1)
def get_token_service(token_repository: RedisTokenRepository):
    return TokenService(token_repository=token_repository)
