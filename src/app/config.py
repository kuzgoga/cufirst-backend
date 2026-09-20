from datetime import timedelta

from pydantic import PostgresDsn, SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pytimeparse.timeparse import timeparse


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "cufirst"
    postgres_password: SecretStr = SecretStr("cufirst")
    postgres_db: str = "cufirst"
    jwt_secret: SecretStr = SecretStr("change-me")
    jwt_algorithm: str = "HS256"
    jwt_expire: str = "1h"

    @field_validator("jwt_expire")
    @classmethod
    def validate_jwt_expire(cls, value: str) -> str:
        seconds = timeparse(value)
        if seconds is None or seconds <= 0:
            raise ValueError("JWT_EXPIRE must be a positive interval, such as 1m, 12h, or 1d")
        return value

    @computed_field
    @property
    def jwt_expire_delta(self) -> timedelta:
        seconds = timeparse(self.jwt_expire)
        if seconds is None:
            raise ValueError("JWT_EXPIRE could not be parsed")
        return timedelta(seconds=seconds)

    @computed_field
    @property
    def database_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )


settings = Settings()
