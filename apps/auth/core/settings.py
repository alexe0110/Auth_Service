from pathlib import Path

from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict

DIR = Path(__file__).resolve(strict=True).parent


class BaseSettings(PydanticBaseSettings):
    model_config = SettingsConfigDict(env_file=DIR.joinpath("./.env"), case_sensitive=True, extra="allow")


class APISettings(BaseSettings):
    TITLE: str = "auth-service"
    OPENAPI_URL: str = "/public/openapi.json"
    DOCS_URL: str = "/public/docs"
    REDOC_URL: str = "/public/redoc"

    LOG_QUERIES: bool = False

    JWT_SECRET_KEY: str
    ACCESS_TOKEN_LIFETIME_SEC: int
    REFRESH_TOKEN_LIFETIME_SEC: int

    class Config:
        env_prefix = "API_"


class RedisSettings(BaseSettings):
    HOST: str
    PORT: int
    DB: str
    URL: str | None = None

    class Config:
        env_prefix = "REDIS_"

    @field_validator("URL", mode="before")
    @classmethod
    def assemble_connection_url(cls, v: str | None, info: FieldValidationInfo) -> str:
        if isinstance(v, str):
            return v

        return RedisDsn.build(  # type: ignore
            scheme="redis",
            host=info.data.get("HOST"),
            port=info.data.get("PORT"),
            path=info.data.get("DB"),
        ).unicode_string()


class PostgresSettings(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DB: str
    POOL_RECYCLE: int
    POOL_SIZE: int
    ECHO: bool
    URL: str | None = None

    class Config:
        env_prefix = "POSTGRES_"

    @field_validator("URL", mode="before")
    @classmethod
    def assemble_connection_url(cls, v: str | None, info: FieldValidationInfo) -> str:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(  # type: ignore
            scheme="postgresql+asyncpg",
            username=info.data.get("USER"),
            password=info.data.get("PASSWORD"),
            host=info.data.get("HOST"),
            port=info.data.get("PORT"),
            path=info.data.get("DB"),
        ).unicode_string()


class Settings(BaseSettings):
    api: APISettings = APISettings()  # type: ignore
    redis: RedisSettings = RedisSettings()  # type: ignore
    postgres: PostgresSettings = PostgresSettings()  # type: ignore


settings = Settings()
