import pytest
import sqlalchemy as sa
from faker import Faker
from fastapi.testclient import TestClient
from httpx import Cookies
from sqlalchemy.orm import Session

from models import Role, Roles
from tests.conftest import _add_user


@pytest.fixture(autouse=True)
def _admin_auth(db_session: Session, client: TestClient, fake: Faker) -> Cookies:
    _add_user(
        db_session,
        fake,
        email="admin@ya.ru",
        password="qwerty",
        roles=[db_session.scalar(sa.select(Roles).where(Roles.id == Role.ADMIN.value))],
    )

    result = client.post(
        "/api/v1/account/login",
        json={
            "email": "admin@ya.ru",
            "password": "qwerty",
        },
    )

    client.cookies = result.cookies
