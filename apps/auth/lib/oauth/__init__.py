from core.settings import settings
from models.exceptions import UnknownExternalProviderError
from models.user_auth import ExternalAuthProviderEnum

from .base import OAuthClient
from .yandex import YandexOAuthClient


def get_provider_client(provider_name: str) -> OAuthClient:
    if provider_name == "yandex":
        return YandexOAuthClient(
            provider_id=ExternalAuthProviderEnum.YANDEX.value,
            client_id=settings.api.YANDEX_OAUTH_CLIENT_ID,
            client_secret=settings.api.YANDEX_OAUTH_CLIENT_SECRET,
            token_url="https://oauth.yandex.ru/token",
            login_url="https://login.yandex.ru/info"
        )

    raise UnknownExternalProviderError
