import sys


from logging.config import fileConfig

from sqlalchemy import pool, engine_from_config


from alembic import context

sys.path = ["", ".."] + sys.path[1:]
from api.db.session import Base  # noqa
from api.core.config import settings  # noqa
from api.models.user_models import *  # noqa
from api.models.app_models import *  # noqa
from api.models.audit_models import *  # noqa
from api.models.events_models import *  # noqa
from api.models.home_models import *  # noqa
from api.models.vk_models import *  # noqa


def get_url():
    user = settings.POSTGRES_USER
    password = settings.POSTGRES_PASSWORD
    host = settings.POSTGRES_HOST
    port = settings.POSTGRES_PORT
    db = settings.POSTGRES_DB
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return url


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url", None)
    if not url:
        url = get_url()

    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    if not config.get_main_option("sqlalchemy.url", None):
        configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
