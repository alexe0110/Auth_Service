from typing import Literal

import pydantic


class YandexTokenData(pydantic.BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    token_type: str


class YandexUserInfo(pydantic.BaseModel):
    id: str
    login: str
    client_id: str
    display_name: str
    real_name: str
    first_name: str
    last_name: str
    sex: Literal["male", "female"]
    default_email: str
    emails: list[str]
    birthday: str
    default_avatar_id: str
    is_avatar_empty: bool
    default_phone: dict
    psuid: str
