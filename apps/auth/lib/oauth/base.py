from httpx import AsyncClient

from .schemas import UserInfo


class OAuthClient:
    def __init__(self, provider_id: str, client_id: str, client_secret: str, token_url: str, login_url: str) -> None:
        self.client = AsyncClient()
        self.provider_id = provider_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.login_url = login_url

    async def get_token(self, code: str) -> str:
        raise NotImplementedError

    async def login(self, token: str) -> UserInfo:
        raise NotImplementedError
