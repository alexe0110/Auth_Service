from http import HTTPStatus
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Query
from jwt import ExpiredSignatureError, PyJWTError

from models.roles import Role
from services.role import RoleService as _RoleService
from services.role import get_role_service
from services.token import TokenService as _TokenService
from services.token import get_token_service
from services.user_account import UserAccountService as _UserAccountService
from services.user_account import get_account_service

UserAccountService = Annotated[_UserAccountService, Depends(get_account_service)]
TokenService = Annotated[_TokenService, Depends(get_token_service)]
RoleService = Annotated[_RoleService, Depends(get_role_service)]


async def valid_refresh_token_data(
    token_service: TokenService,
    refresh_token: Annotated[str, Cookie(include_in_schema=False)],
):
    try:
        decoded = token_service.decode_token(refresh_token)
    except PyJWTError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid Token") from e
    return decoded


async def valid_access_token_data(
    token_service: TokenService,
    access_token: Annotated[str | None, Cookie(include_in_schema=False)],
):
    if not access_token:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Authorization required") from None

    try:
        decoded = token_service.decode_token(access_token)
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Authorization required") from e
    except PyJWTError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid Token") from e
    return decoded


def role_required(role: Role):
    def wrapper(
        access_token: Annotated[str, Cookie(include_in_schema=False)],
        token_service: TokenService,
    ):
        try:
            decoded = token_service.decode_token(access_token)
        except ExpiredSignatureError as e:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Authorization required") from e
        if role.value not in [r["id"] for r in decoded["roles"]]:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden") from None

    return wrapper


class PaginateQueryParams:
    def __init__(
        self,
        page_number: int = Query(
            1,
            title="Page number",
            description="Page number to return",
            ge=1,
        ),
        page_size: int = Query(
            50,
            title="Size of page",
            description="The number of records returned per page",
            ge=1,
            le=500,
        ),
    ):
        self.page_number = page_number
        self.page_size = page_size
