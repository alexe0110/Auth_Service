import abc
from uuid import UUID

import sqlalchemy as sa

from db.postgres import AsyncSession
from models import Roles
from models.exceptions import RoleAlreadyExistError


class RoleRepository(abc.ABC):
    @abc.abstractmethod
    async def get_role(self, session: AsyncSession, role_id: UUID) -> Roles | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_all_roles(self, session: AsyncSession):
        raise NotImplementedError

    @abc.abstractmethod
    async def create_role(self, session: AsyncSession, name: str) -> Roles:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_role(self, session: AsyncSession, role_id: UUID, new_name: str) -> Roles | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_role(self, session: AsyncSession, role_id: UUID) -> bool:
        raise NotImplementedError


class PostgresRolesRepository(RoleRepository):
    async def get_role(self, session: AsyncSession, role_id: UUID) -> Roles | None:
        result = await session.get(Roles, role_id)

        return result

    async def get_all_roles(self, session: AsyncSession):
        result = await session.scalars(sa.select(Roles))

        return result.fetchall()

    async def create_role(self, session: AsyncSession, name: str) -> Roles:
        data = Roles(name=name)

        if await session.scalar(sa.select(Roles).where(Roles.name == name)):
            raise RoleAlreadyExistError

        session.add(data)
        await session.flush()

        return data

    async def update_role(self, session: AsyncSession, role_id: UUID, new_name: str) -> Roles | None:
        stmt = sa.update(Roles).where(Roles.id == role_id).values(name=new_name)
        await session.execute(stmt)

        if result := await session.get(Roles, role_id):
            return result

    async def delete_role(self, session: AsyncSession, role_id: UUID) -> bool:
        if result := await session.get(Roles, role_id):
            await session.delete(result)
            await session.flush()
            return True

        return False
