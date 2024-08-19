import base64
from http import HTTPStatus

from .base import OAuthClient
from .exceptions import OAuthGetTokenError, OAuthLoginError
from .schemas import UserInfo, YandexUserInfo


class YandexOAuthClient(OAuthClient):
    def __init__(self, provider_id: str, client_id: str, client_secret: str, token_url: str, login_url: str) -> None:
        super().__init__(provider_id, client_id, client_secret, token_url, login_url)

    def _get_authorization_header(self) -> str:
        return f"Basic {base64.b64encode(
            bytes(f"{self.client_id}:{self.client_secret}", encoding="utf-8")
        ).decode("utf-8")}"

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
            raise OAuthGetTokenError

        resp_json: dict = resp.json()
        return resp_json.get("access_token")

    async def login(self, token: str):
        resp = await self.client.get(
            url=self.login_url,
            params={"format": "json"},
            headers={"Authorization": f"OAuth {token}"}
        )

        if not HTTPStatus(resp.status_code).is_success:
            raise OAuthLoginError

        data = YandexUserInfo(**resp.json())

        return UserInfo.model_validate({
            "id": data.id,
            "email": data.default_email,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "middle_name": None,
            "gender": data.sex,
            "birthdate": data.birthday
        })
