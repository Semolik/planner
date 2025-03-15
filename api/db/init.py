from models.app import AppSettings
from fastapi.logger import logger
from models.user import User
from sqlalchemy import select
from db.session import async_session_maker


async def init_db():
    async with async_session_maker() as session:
        await init_settings(session)
        select_first_superuser = select(User).where(User.is_superuser == True)
        result = await session.execute(select_first_superuser)
        if not result.scalar():
            logger.warning(
                "Ожидается регистрация администратора (первый зарегистрированный пользователь будет администратором)")


async def init_settings(session):
    query = select(AppSettings)
    result = await session.execute(query)
    settings = result.scalars().all()
    app_name = list(filter(lambda x: x.key == 'app_name', settings))
    if not app_name:
        session.add(AppSettings(key='app_name', value='Планировщик'))
        await session.commit()
        logger.warning(
            "\033[93mУстановлено стандартное название приложения 'Планировщик'\033[0m")
    app_logo = list(filter(lambda x: x.key == 'app_logo', settings))
    if not app_logo or not app_logo[0].value:
        logger.warning(
            "\033[93mВнимание: Логотип приложения не установлен\033[0m")
    await session.commit()
