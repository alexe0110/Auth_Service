from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from api.v1.dependencies import RoleService, role_required
from db.postgres import AsyncSession, get_postgres_session
from models.exceptions import RoleAlreadyExistError
from models.roles import Role
from schemas.roles import RoleCreateRequest, RoleSchema, RoleUpdateRequest

role_router = APIRouter(prefix="/role", tags=["Role"])


@role_router.get(
    "/",
    response_model=list[RoleSchema | None],
    dependencies=[Depends(role_required(Role.ADMIN))],
    summary="Получить список всех ролей",
    description="Доступ только для админской роли",
)
async def get_all_roles(role_service: RoleService, db_session: Annotated[AsyncSession, Depends(get_postgres_session)]):
    result = await role_service.get_all_roles(session=db_session)

    return result


@role_router.get(
    "/{role_id}",
    response_model=RoleSchema,
    dependencies=[Depends(role_required(Role.ADMIN))],
    summary="Получить роль по id",
    description="Доступ только для админской роли",
)
async def get_role(
    role_service: RoleService, db_session: Annotated[AsyncSession, Depends(get_postgres_session)], role_id: UUID
):
    result = await role_service.get_role(session=db_session, role_id=role_id)

    if not result:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"detail": "Role not found"},
        )

    return result


@role_router.post(
    "/",
    response_model=RoleSchema,
    dependencies=[Depends(role_required(Role.ADMIN))],
    summary="Создавние новой роли",
    description="Доступ только для админской роли",
)
async def create_role(
    role_service: RoleService,
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    body: RoleCreateRequest,
):
    try:
        result = await role_service.create_role(session=db_session, name=body.name)
    except RoleAlreadyExistError as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"detail": e.msg})

    return result


@role_router.patch(
    "/{role_id}",
    response_model=RoleSchema,
    dependencies=[Depends(role_required(Role.ADMIN))],
    summary="Обновление данных роли",
    description="Доступ только для админской роли",
)
async def update_role(
    role_service: RoleService,
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    body: RoleUpdateRequest,
    role_id: UUID,
):
    result = await role_service.update_role(session=db_session, role_id=role_id, new_name=body.new_name)

    if not result:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"detail": "Role not found"},
        )

    return result


@role_router.delete(
    "/{role_id}",
    dependencies=[Depends(role_required(Role.ADMIN))],
    summary="Удаление роли",
    description="Доступ только для админской роли",
)
async def delete_role(
    role_service: RoleService,
    db_session: Annotated[AsyncSession, Depends(get_postgres_session)],
    role_id: UUID,
):
    if await role_service.delete_role(session=db_session, role_id=role_id):
        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={"detail": f"Role {role_id} was be deleted"},
        )

    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"detail": "Role not found"},
    )
