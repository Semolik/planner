import contextlib
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from api.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.POSTGRES_DATABASE_URI.unicode_string(),
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


get_async_session_context = contextlib.asynccontextmanager(get_async_session)
