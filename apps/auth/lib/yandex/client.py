import base64
from http import HTTPStatus

from httpx import AsyncClient

from core.settings import settings
from lib.yandex.schemas import YandexTokenData, YandexUserInfo

from .exceptions import YandexGettingOAuthTokenError, YandexOAuthLoginError


class YandexHTTPClient:
    authorization_url = "https://oauth.yandex.ru/authorize"
    token_url = "https://oauth.yandex.ru/token"
    login_url = "https://login.yandex.ru/info"

    def __init__(self) -> None:
        self.client = AsyncClient()
        self.client_id = settings.api.YANDEX_OAUTH_CLIENT_ID
        self.client_secret = settings.api.YANDEX_OAUTH_CLIENT_SECRET

    def _get_authorization_header(self) -> str:
        return f"Basic {base64.b64encode(
            bytes(f"{self.client_id}:{self.client_secret}", encoding="utf-8")
        ).decode("utf-8")}"

    async def authorize(self):
        await self.client.get(url=self.authorization_url, params={
            "response_type": "code",
            "client_id": self.client_id,
            "scope": "login:birthday login:email login:info"
        })

    async def get_token(self, code: str):
        resp = await self.client.post(
            url=self.token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
            },
            headers={
                "Authorization": self._get_authorization_header(),
                "Content-type": "application/x-www-form-urlencoded"
            }
        )

        if not HTTPStatus(resp.status_code).is_success:
            raise YandexGettingOAuthTokenError

        return YandexTokenData(**resp.json())

    async def login(self, oauth_token: str):
        resp = await self.client.get(
            url=self.login_url,
            params={"format": "json"},
            headers={"Authorization": f"OAuth {oauth_token}"}
        )

        if not HTTPStatus(resp.status_code).is_success:
            raise YandexOAuthLoginError

        return YandexUserInfo(**resp.json())
