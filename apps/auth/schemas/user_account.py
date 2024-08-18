from datetime import date, datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import EmailStr, model_validator

from .base import FromCamelCase, PydanticBase, ToCamelCase
from .roles import RoleSchema


class RegisterUserIn(FromCamelCase):
    email: EmailStr
    password: str
    last_name: str
    first_name: str
    middle_name: str | None = None
    birthdate: date
    gender: Literal["male", "female"]


class UserAccountSchema(PydanticBase):
    id: UUID
    email: EmailStr
    last_name: str
    first_name: str
    middle_name: str | None
    birthdate: date
    gender: str
    roles: list[RoleSchema]


class LoginUserIn(FromCamelCase):
    email: EmailStr
    password: str


class ChangeCredentialsIn(FromCamelCase):
    email: EmailStr | None = None
    password: str | None = None

    @model_validator(mode="after")
    def check_at_least_one_value_exists(self) -> Self:
        if not any((self.email, self.password)):
            raise ValueError("password or email required")
        return self


class UserAccountOut(UserAccountSchema, ToCamelCase):
    pass


class UserAccountLoginHistorySchema(PydanticBase):
    id: UUID
    user_agent: str
    login_time: datetime


class UserAccountLoginHistoryOut(UserAccountLoginHistorySchema, ToCamelCase):
    pass


class LoginUserViaExternalProviderSchema(PydanticBase):
    id: str
    email: str
    first_name: str
    last_name: str
    middle_name: str | None = None
    gender: Literal["male", "female"]
    birthdate: date
