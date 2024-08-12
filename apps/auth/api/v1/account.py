from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Cookie, Depends, Header, HTTPException, Response

from db.postgres import AsyncSession, get_postgres_session
from models.exceptions import (
    GenerateTokensError,
    InvalidCredentialsError,
    RoleNotExistError,
    UserAlreadyExistError,
    UserNotExistsError,
    UserNotRegisteredError,
    UserRoleAlreadyExistError,
    UserRoleNotExistError,
)
from models.roles import Role
from schemas.user_account import (
    ChangeCredentialsIn,
    LoginUserIn,
    RegisterUserIn,
    UserAccountLoginHistoryOut,
    UserAccountOut,
)
from schemas.user_roles import UserRole

from .dependencies import (
    PaginateQueryParams,
    TokenService,
    UserAccountService,
    role_required,
    security_jwt_cookie,
    valid_refresh_token_data,
)

user_account_router = APIRouter(prefix="/account", tags=["Account"])


@user_account_router.post(
    "/register",
    response_model=UserAccountOut,
    summary="Регистрация нового пользователя",
)
async def register_user(
    register_user_dto: Annotated[RegisterUserIn, Body()],
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    user_account_service: UserAccountService,
    token_service: TokenService,
    response: Response,
    user_agent: Annotated[str, Header(include_in_schema=False)] = "unknown",
):
    try:
        registered_user = await user_account_service.register(
            session=db_session, data=register_user_dto, user_agent=user_agent
        )
        access_token, refresh_token = await token_service.create_session(
            account_id=registered_user.id,
            access_token_data={
                "account_id": str(registered_user.id),
                "roles": [role.model_dump(mode="json") for role in registered_user.roles],
            },
            refresh_token_data={"account_id": str(registered_user.id)},
        )
    except UserAlreadyExistError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=e.msg) from e
    except GenerateTokensError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=e.msg) from e

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return registered_user


@user_account_router.post(
    "/login",
    response_model=UserAccountOut,
    summary="Вход пользователя в аккаунт",
    description="Вход пользователя в аккаунт по логину и паролю",
)
async def login_user(
    login_user_dto: Annotated[LoginUserIn, Body()],
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    user_account_service: UserAccountService,
    token_service: TokenService,
    response: Response,
    user_agent: Annotated[str, Header(include_in_schema=False)] = "unknown",
):
    try:
        account = await user_account_service.login(session=db_session, data=login_user_dto, user_agent=user_agent)
        access_token, refresh_token = await token_service.create_session(
            account_id=account.id,
            access_token_data={
                "account_id": str(account.id),
                "roles": [role.model_dump(mode="json") for role in account.roles],
            },
            refresh_token_data={"account_id": str(account.id)},
        )
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=e.msg) from e
    except GenerateTokensError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=e.msg) from e

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return account


@user_account_router.post(
    "/logout",
    summary="Выход пользователя из аккаунта",
)
async def logout(
    token_service: TokenService,
    response: Response,
    refresh_token: Annotated[str | None, Cookie(include_in_schema=False)] = None,
):
    if not refresh_token:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Authorization required") from None

    await token_service.delete_session(refresh_token)

    response.delete_cookie(key="access_token", httponly=True)
    response.delete_cookie(key="refresh_token", httponly=True)

    response.status_code = HTTPStatus.NO_CONTENT
    return response


@user_account_router.get("/refresh_tokens", summary="Обмен refresh токена на новую пару access и refresh токенов")
async def refresh_tokens(
    token_service: TokenService,
    user_account_service: UserAccountService,
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    response: Response,
    decoded_token: Annotated[dict, Depends(valid_refresh_token_data)],
):
    try:
        account = await user_account_service.get_by_id(session=db_session, account_id=decoded_token["account_id"])

        new_access_token, new_refresh_token = await token_service.create_session(
            account_id=account.id,
            access_token_data={
                "account_id": str(account.id),
                "roles": [role.model_dump(mode="json") for role in account.roles],
            },
            refresh_token_data={"account_id": str(account.id)},
        )
    except GenerateTokensError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=e.msg) from e
    except UserNotExistsError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=e.msg) from e

    response.set_cookie(key="access_token", value=new_access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True)

    response.status_code = HTTPStatus.NO_CONTENT
    return response


@user_account_router.patch(
    "/credentials", response_model=UserAccountOut, summary="Изменения логина или пароля аккаунта"
)
async def change_credentials(
    change_credentials_dto: Annotated[ChangeCredentialsIn, Body()],
    user_account_service: UserAccountService,
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    user: Annotated[dict, Depends(security_jwt_cookie)],
):
    try:
        return await user_account_service.change_credentials(
            session=db_session, account_id=user["account_id"], data=change_credentials_dto
        )
    except UserAlreadyExistError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User with same email already exists") from e


@user_account_router.get(
    "/login_history", response_model=list[UserAccountLoginHistoryOut], summary="Получение истории входов в аккаунт"
)
async def get_user_login_history(
    user_account_service: UserAccountService,
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    user: Annotated[dict, Depends(security_jwt_cookie)],
    pagination: PaginateQueryParams = Depends(),
):
    return await user_account_service.get_login_history(
        session=db_session,
        account_id=user["account_id"],
        page_number=pagination.page_number,
        page_size=pagination.page_size,
    )


@user_account_router.get(
    "/{account_id}/roles",
    response_model=list[UserRole | None],
    dependencies=[Depends(role_required(Role.ADMIN)), Depends(security_jwt_cookie)],
)
async def get_user_roles(
    user_account_service: UserAccountService,
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    account_id: UUID,
):
    roles = await user_account_service.get_user_roles(session=db_session, user_id=account_id)

    return roles


@user_account_router.get(
    "/{account_id}/roles/{role_id}",
    response_model=None,
    dependencies=[Depends(role_required(Role.ADMIN)), Depends(security_jwt_cookie)],
    summary="Проверка наличия роли у пользователя",
    description="Доступ только для админской роли",
)
async def check_have_user_role(
    user_account_service: UserAccountService,
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    account_id: UUID,
    role_id: UUID,
):
    have = await user_account_service.check_user_role(session=db_session, account_id=account_id, role_id=role_id)
    if not have:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User does not have the requested role")

    return Response(status_code=HTTPStatus.NO_CONTENT)


@user_account_router.post(
    "/{account_id}/roles",
    response_model=list[UserRole],
    dependencies=[Depends(role_required(Role.ADMIN)), Depends(security_jwt_cookie)],
    summary="Добавление роли пользователю",
    description="Доступ только для админской роли",
)
async def assign_user_role(
    user_account_service: UserAccountService,
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    account_id: UUID,
    role_ids: Annotated[list[UUID], Body()],
):
    try:
        result = await user_account_service.assign_user_role(
            session=db_session, role_ids=role_ids, account_id=account_id
        )
    except (UserNotRegisteredError, RoleNotExistError) as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.msg) from e
    except UserRoleAlreadyExistError as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=e.msg) from e

    return result


@user_account_router.delete(
    "/{account_id}/roles/{role_id}",
    response_model=list[UserRole],
    dependencies=[Depends(role_required(Role.ADMIN)), Depends(security_jwt_cookie)],
    summary="Удаление роли у пользователя",
    description="Доступ только для админской роли",
)
async def unassign_user_role(
    user_account_service: UserAccountService,
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    account_id: UUID,
    role_id: UUID,
):
    try:
        result = await user_account_service.unassign_user_role(
            session=db_session, account_id=account_id, role_id=role_id
        )
    except UserRoleNotExistError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.msg) from e

    return result
