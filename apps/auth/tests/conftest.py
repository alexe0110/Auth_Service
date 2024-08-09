import asyncio
import uuid

import bcrypt
import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from core.settings import settings
from db import postgres, redis
from main import app
from models import Role, Roles, UserAccount, UserAuth, UserLoginHistory, UserRoles

test_dsn = (
    f"postgresql+psycopg2://{settings.postgres.USER}:{settings.postgres.PASSWORD}"
    f"@{settings.postgres.HOST}:5434/{settings.postgres.DB}"
)
engine: Engine = create_engine(test_dsn)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def _make_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_dsn)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def client() -> TestClient:
    postgres.setup_postgres_connection()
    redis.setup_redis_connection()
    yield TestClient(app)
    redis.close_redis_connection()
    postgres.close_postgres_connection()


@pytest.fixture()
def db_session():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()


@pytest.fixture()
def fake():
    return Faker()


@pytest.fixture(autouse=True)
def _clear_db(db_session: Session):
    [
        db_session.execute(stmt)
        for stmt in [
            sa.delete(Roles).where(Roles.id.notin_([role.value for role in Role])),
            sa.delete(UserAccount),
            sa.delete(UserRoles),
            sa.delete(UserAuth),
            sa.delete(UserLoginHistory),
        ]
    ]
    db_session.commit()


@pytest.fixture()
def add_role(db_session: Session, fake):
    role_id = uuid.uuid4()
    role = Roles(id=role_id, name=fake.word())

    db_session.add(role)
    db_session.commit()

    return str(role_id)


@pytest.fixture()
def email(fake: Faker):
    return fake.email()


@pytest.fixture()
def password(fake: Faker):
    return fake.password()


def _add_user(db_session: Session, fake: Faker, email, password, roles: list | None = None) -> uuid.UUID:
    user_account_id = uuid.uuid4()

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode()

    acc = UserAccount(
        id=user_account_id,
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        middle_name=fake.first_name(),
        gender="male",
        birthdate=fake.date_object(),
        roles=roles or [],
    )

    auth = UserAuth(email=email, password=hashed_password, account=acc)

    db_session.add(auth)
    db_session.commit()

    return user_account_id


@pytest.fixture()
def add_user(db_session: Session, fake: Faker, email, password) -> str:
    user_account_id = _add_user(db_session, fake, email, password)
    return str(user_account_id)


pytest_plugins = ["tests.prepare"]
