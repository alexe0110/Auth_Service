from functools import lru_cache
from uuid import UUID

from db.postgres import AsyncSession
from repositories import RoleRepository
from services.dependencies import PostgresRolesRepository


class RoleService:
    def __init__(self, role_repository: RoleRepository) -> None:
        self.role_repository = role_repository

    async def get_role(self, session: AsyncSession, role_id: UUID):
        role = await self.role_repository.get_role(session, role_id)

        return role

    async def get_all_roles(self, session: AsyncSession):
        roles = await self.role_repository.get_all_roles(session)

        return roles

    async def create_role(self, session: AsyncSession, name: str):
        role = await self.role_repository.create_role(session, name)

        return role

    async def update_role(self, session: AsyncSession, role_id: UUID, new_name: str):
        role = await self.role_repository.update_role(session, role_id, new_name)

        return role

    async def delete_role(self, session: AsyncSession, role_id: UUID):
        role = await self.role_repository.delete_role(session, role_id)

        return role


@lru_cache(maxsize=1)
def get_role_service(
    role_repository: PostgresRolesRepository,
):
    return RoleService(role_repository)
