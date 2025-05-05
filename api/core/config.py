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
    EVENT_LEVELS: List[str] = [
        'Институтский', 'Городской', 'Университетский',
        'Региональный', 'Окружной', 'Межрегиональный',
        'Всероссийский', 'Международный'
    ]
    # Количество дней на обработку репортажа считая со следующего дня после события
    PHOTOGRAPHERS_DEADLINE_DEFAULT: int = 3
    COPYWRITERS_DEADLINE_DEFAULT: int = 4  # Количество дней на создание текста
    # Количество дней на создание обложки на альбом (дни после выгрузки репортажа)
    DESIGNERS_DEADLINE_DEFAULT: int = 2

    @property
    def POSTGRES_URI(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

    @property
    def BACKEND_CORS_ORIGINS_LIST(self) -> List[str]:
        return self.BACKEND_CORS_ORIGINS.split(',')

    class Config:
        case_sensitive = True


settings = Settings()
