from datetime import datetime

import bcrypt
import click
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.settings import settings
from models import Role, Roles, UserAccount, UserAuth


@click.command(short_help="Create superuser")
@click.option("--email", "-e", help="EMail address")
@click.option("--password", "-p", help="Password to access")
@click.option("--first_name", default="Ivan", help="First name")
@click.option("--last_name", default="Ivanov", help="Last name")
@click.option("--middle_name", default="Ivanovich", help="Middle name")
@click.option("--gender", default="male", help="male or female")
@click.option("--birthdate", default="01.01.1970", help="Birth date, format %d.%m.%Y")
def add_superuser(email: str, password: str, first_name: str, last_name: str, middle_name: str, gender: str, birthdate):
    dsn = (
        f"postgresql+psycopg2://{settings.postgres.USER}:{settings.postgres.PASSWORD}"
        f"@{settings.postgres.HOST}:{settings.postgres.PORT}/{settings.postgres.DB}"
    )
    engine = create_engine(dsn)

    with Session(engine) as session:
        admin_role = session.scalar(select(Roles).where(Roles.id == Role.ADMIN.value))
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode()

        acc = UserAccount(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            gender=gender,
            birthdate=datetime.strptime(birthdate, "%d.%m.%Y").date(),
            roles=[admin_role],
        )

        auth = UserAuth(email=email, password=hashed_password, account=acc)

        try:
            session.add(auth)
            session.commit()
            click.secho(f"\nSuperuser {email} is ready!", fg="green")
        except IntegrityError:
            session.rollback()
            click.secho(f"User with email {email} already exists", fg="red")
        finally:
            session.close()


@click.group(
    short_help="CLI for work with the authorization service", context_settings={"help_option_names": ["-h", "--help"]}
)
def auth_cli() -> None:
    pass


auth_cli.add_command(add_superuser)
