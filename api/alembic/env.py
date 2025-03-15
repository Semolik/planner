import asyncio
from logging.config import fileConfig

import asyncpg
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from config import settings

from alembic import context
from models.app import *
from models.user import *
from models.files import *
from models.events import *
from db.session import Base
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", settings.POSTGRES_URI)
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    # await connectable.dispose()
    # # conn_str = f"postgres://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/postgres"
    # # conn = await asyncpg.connect(conn_str)
    # # db_exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname=$1", settings.POSTGRES_DB)
    # # if not db_exists:
    # #     print("Database does not exist. Creating...")
    # #     await conn.execute(f"CREATE DATABASE {settings.POSTGRES_DB}")
    # # await conn.close()
    # # connectable = async_engine_from_config(
    # #     config.get_section(config.config_ini_section, {}),
    # #     prefix="sqlalchemy.",
    # #     poolclass=pool.NullPool,
    # # )

    # # async with connectable.connect() as connection:
    # #     await connection.run_sync(do_run_migrations)
    # async with connectable.connect() as connection:
    #     #     try:
    #     #         await connectio..fetchval(
    #     #             "SELECT 1 FROM pg_database WHERE datname=$1", settings.POSTGRES_DB
    #     #         )
    #     #     except Exception as e:
    #     #         print("Database does not exist", e)
    #     #         await connection.close()

    #     #         conn = await asyncpg.connect(conn_str)
    #     #         await conn.execute(f"CREATE DATABASE {settings.POSTGRES_DB}")
    #     #         await conn.close()
    #     #         connectable = async_engine_from_config(
    #     #             config.get_section(config.config_ini_section, {}),
    #     #             prefix="sqlalchemy.",
    #     #             poolclass=pool.NullPool,
    #     #         )
    #     #         connection = await connectable.connect()
    #     try:
    #         await connection.run_sync(do_run_migrations)
    #     except Exception as e:
    #         target_metadata.create_all(connectable)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
