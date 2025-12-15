import secrets
from typing import List

from pydantic import PostgresDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="allow",
    )
    DEV_MODE: bool = True
    SECRET: str
    BACKEND_CORS_ORIGINS: str
    API_DOMAIN: str
    API_PORT: int
    COOKIE_DOMAIN: str
    EVENT_LEVELS: List[str] = [
        "Институтский",
        "Университетский",
        "Городской",
        "Региональный",
        "Окружной",
        "Межрегиональный",
        "Всероссийский",
        "Международный",
        "Другое",
    ]
    # Количество дней на обработку репортажа считая со следующего дня после события
    PHOTOGRAPHERS_DEADLINE_DEFAULT: int = 3
    COPYWRITERS_DEADLINE_DEFAULT: int = 4  # Количество дней на создание текста
    # Количество дней на создание обложки на альбом (дни после выгрузки репортажа)
    DESIGNERS_DEADLINE_DEFAULT: int = 2
    VK_APP: int
    HOST: str
    FIRST_INSTITUTE: str
    FIRST_ADMIN_USERNAME: str
    FIRST_ADMIN_PASSWORD: str
    # PostgresSQL Configuration
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    POSTGRES_DATABASE_URI: PostgresDsn | None = None

    @field_validator("POSTGRES_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(
        cls,
        v: str | None,
        values: ValidationInfo,
    ) -> PostgresDsn:
        if isinstance(v, str):
            return v

        options = {
            "scheme": "postgresql+asyncpg",
            "username": values.data.get("POSTGRES_USER"),
            "password": values.data.get("POSTGRES_PASSWORD"),
            "host": values.data.get("POSTGRES_HOST"),
            "port": values.data.get("POSTGRES_PORT"),
            "path": f"{values.data.get('POSTGRES_DB') or ''}",
        }
        return PostgresDsn.build(**options)

    @property
    def BACKEND_CORS_ORIGINS_LIST(self) -> List[str]:
        return self.BACKEND_CORS_ORIGINS.split(",")


settings = Settings()
