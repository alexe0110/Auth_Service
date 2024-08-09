from typing import Annotated

from fastapi import Depends

from repositories.account import PostgresUserAccountRepository as _PostgresUserAccountRepository
from repositories.role import PostgresRolesRepository as _PostgresRolesRepository
from repositories.token import RedisTokenRepository as _RedisTokenRepository

PostgresUserAccountRepository = Annotated[_PostgresUserAccountRepository, Depends(_PostgresUserAccountRepository)]
PostgresRolesRepository = Annotated[_PostgresRolesRepository, Depends(_PostgresRolesRepository)]
RedisTokenRepository = Annotated[_RedisTokenRepository, Depends(_RedisTokenRepository)]
