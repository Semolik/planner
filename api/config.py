import secrets
from typing import List

from pydantic import PostgresDsn, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET: str = secrets.token_urlsafe(32)
    BACKEND_CORS_ORIGINS: str
    API_DOMAIN: str
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def POSTGRES_URI(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

    @property
    def BACKEND_CORS_ORIGINS_LIST(self) -> List[str]:
        return self.BACKEND_CORS_ORIGINS.split(',')

    class Config:
        case_sensitive = True


settings = Settings()
