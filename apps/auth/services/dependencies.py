from typing import Annotated

from fastapi import Depends

from lib.yandex.client import YandexHTTPClient as _YandexHTTPClient
from repositories.account import PostgresUserAccountRepository as _PostgresUserAccountRepository
from repositories.role import PostgresRolesRepository as _PostgresRolesRepository
from repositories.token import RedisTokenRepository as _RedisTokenRepository

PostgresUserAccountRepository = Annotated[_PostgresUserAccountRepository, Depends(_PostgresUserAccountRepository)]
PostgresRolesRepository = Annotated[_PostgresRolesRepository, Depends(_PostgresRolesRepository)]
RedisTokenRepository = Annotated[_RedisTokenRepository, Depends(_RedisTokenRepository)]
YandexHTTPClient = Annotated[_YandexHTTPClient, Depends(_YandexHTTPClient)]
