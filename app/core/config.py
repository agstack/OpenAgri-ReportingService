from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
from password_validator import PasswordValidator

from typing import Optional, Any, List

from os import path, environ


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [ ]

    PROJECT_ROOT: str = path.dirname(path.dirname(path.realpath(__file__)))

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values) -> Any:
        if isinstance(v, str):
            return v

        url = "postgresql://{}:{}@{}:{}/{}".format(
            environ.get("POSTGRES_USER"),
            environ.get("POSTGRES_PASSWORD"),
            environ.get("POSTGRES_HOST"),
            environ.get("POSTGRES_PORT"),
            environ.get("POSTGRES_DB")
        )

        return url

    PASSWORD_SCHEMA_OBJ: PasswordValidator = PasswordValidator()
    PASSWORD_SCHEMA_OBJ \
        .min(8) \
        .max(100) \
        .has().uppercase() \
        .has().lowercase() \
        .has().digits() \
        .has().no().spaces() \

    ACCESS_TOKEN_EXPIRATION_TIME: int
    JWT_KEY: str = "c2bab29d257f0ffc52d9ac677d4ff6d1d9d5e92e3d3939d3f4cwc"


settings = Settings()
