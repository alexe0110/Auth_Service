import http
import time
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Query, Request
from fastapi.security import APIKeyCookie

from services.film import FilmService as _FilmService
from services.film import get_film_service
from services.genre import GenreService as _GenreService
from services.genre import get_genre_service
from services.person import PersonService as _PersonService
from services.person import get_person_service
from settings.api import api_settings

FilmService = Annotated[_FilmService, Depends(get_film_service)]
GenreService = Annotated[_GenreService, Depends(get_genre_service)]
PersonService = Annotated[_PersonService, Depends(get_person_service)]


def decode_token(token: str):
    try:
        decoded_token = jwt.decode(token, api_settings.API_JWT_SECRET_KEY, algorithms=["HS256"])
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except Exception:
        return None


class JWTBearerCookie(APIKeyCookie):
    def __init__(self, auto_error: bool = True):
        super().__init__(name="access_token", auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        cookie_token: str | None = await super().__call__(request)
        if not cookie_token:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail="Missing authorization cookie.")
        decoded_token = self.parse_token(cookie_token)
        if not decoded_token:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail="Invalid or expired token.")
        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> dict | None:
        return decode_token(jwt_token)


security_jwt_cookie = JWTBearerCookie()


class PaginateQueryParams:
    def __init__(
        self,
        page_number: int = Query(
            1,
            title="Page number.",
            description="Page number to return",
            ge=1,
        ),
        page_size: int = Query(
            50,
            title="Size of page.",
            description="The number of records returned per page",
            ge=1,
            le=500,
        ),
    ):
        self.page_number = page_number
        self.page_size = page_size
