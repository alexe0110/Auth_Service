from uuid import UUID

from .base import PydanticBase


class UserRole(PydanticBase):
    id: UUID
    user_account_id: UUID
    role_id: UUID
