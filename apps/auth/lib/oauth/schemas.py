from datetime import date
from typing import Literal

from pydantic import BaseModel


class UserInfo(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    middle_name: str | None = None
    gender: Literal["male", "female"]
    birthdate: date


class YandexUserInfo(BaseModel):
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
