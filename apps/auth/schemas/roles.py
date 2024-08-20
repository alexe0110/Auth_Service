from uuid import UUID

from .base import PydanticBase


class RoleSchema(PydanticBase):
    id: UUID
    name: str


class RoleCreateRequest(PydanticBase):
    name: str


class RoleUpdateRequest(PydanticBase):
    new_name: str
