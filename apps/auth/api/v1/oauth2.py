from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response

from db.postgres import AsyncSession, get_postgres_session
from lib.oauth.exceptions import OAuthBaseError
from models.exceptions import GenerateTokensError, UnknownExternalProviderError
from schemas.user_account import UserAccountOut

from .dependencies import TokenService, UserAccountService

oauth2_router = APIRouter(prefix="/oauth2", tags=["OAuth2"])


@oauth2_router.get(
    "/{provider}/end",
    response_model=UserAccountOut,
    summary="Авторизация через сторонний сервис",
)
async def yandex_callback(
    account_service: UserAccountService,
    token_service: TokenService,
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    response: Response,
    provider: str,
    code: str = Query(),
    user_agent: Annotated[str, Header(include_in_schema=False)] = "unknown",
):
    try:
        account = await account_service.login_via_external_provider(
            session=db_session,
            provider=provider,
            code=code,
            user_agent=user_agent
        )
        access_token, refresh_token = await token_service.create_session(
            account_id=account.id,
            access_token_data={
                "account_id": str(account.id),
                "roles": [role.model_dump(mode="json") for role in account.roles],
            },
            refresh_token_data={"account_id": str(account.id)},
        )
    except OAuthBaseError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="OAuth exception occured") from e
    except UnknownExternalProviderError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Unknown external provider") from e
    except GenerateTokensError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=e.msg) from e

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return account
