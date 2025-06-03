from models.app_models import AppSettings
from models.events_models import EventLevel, TasksToken
from fastapi.logger import logger
from models.user_models import User, UserRole
from sqlalchemy import select
from db.session import async_session_maker
import uuid
from core.config import settings


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
    settings_list = result.scalars().all()
    app_name = list(filter(lambda x: x.key == 'app_name', settings_list))
    if not app_name:
        session.add(AppSettings(key='app_name', value='Планировщик'))
        logger.warning(
            "\033[93mУстановлено стандартное название приложения 'Планировщик'\033[0m")
    app_logo = list(filter(lambda x: x.key == 'app_logo', settings_list))
    if not app_logo or not app_logo[0].value:
        logger.warning(
            "\033[93mВнимание: Логотип приложения не установлен\033[0m")
    tasks_tokens = (await session.execute(select(TasksToken))).scalars().all()
    for role in UserRole:
        if not any(x.role == role for x in tasks_tokens):
            token = uuid.uuid4()
            session.add(TasksToken(role=role, token=str(token)))
            logger.warning(
                f"\033[93mУстановлен токен для доступа к задачам для роли {role}: {token}\033[0m")
    levels_configured = next(
        (x for x in settings_list if x.key == 'levels_configured'), None)
    if not levels_configured or levels_configured.value.lower() != 'true':
        event_levels = (await session.execute(select(EventLevel))).scalars().all()
        for level in settings.EVENT_LEVELS:
            if not any(x.name == level for x in event_levels):
                session.add(EventLevel(name=level))
                logger.warning(
                    f"\033[93mДобавлен уровень события: {level}\033[0m")
        if not levels_configured:
            session.add(AppSettings(key='levels_configured', value='true'))
        else:
            levels_configured.value = 'true'
    photographers_deadline = next(
        (x for x in settings_list if x.key == 'photographers_deadline'), None)
    if not photographers_deadline:
        session.add(AppSettings(key='photographers_deadline',
                    value=str(settings.PHOTOGRAPHERS_DEADLINE_DEFAULT)))
        logger.warning(
            f'\033[93mУстановлено стандартное количество дней на обработку репортажа: {settings.PHOTOGRAPHERS_DEADLINE_DEFAULT}\033[0m')
    copywriters_deadline = next(
        (x for x in settings_list if x.key == 'copywriters_deadline'), None)
    if not copywriters_deadline:
        session.add(AppSettings(key='copywriters_deadline',
                    value=str(settings.COPYWRITERS_DEADLINE_DEFAULT)))
        logger.warning(
            f'\033[93mУстановлено стандартное количество дней на написание текстов: {settings.COPYWRITERS_DEADLINE_DEFAULT}\033[0m')
    designers_deadline = next(
        (x for x in settings_list if x.key == 'designers_deadline'), None)
    if not designers_deadline:
        session.add(AppSettings(key='designers_deadline',
                    value=str(settings.DESIGNERS_DEADLINE_DEFAULT)))
        logger.warning(
            f'\033[93mУстановлено стандартное количество дней на создание обложки на альбом (дней после выгрузки репортажа): {settings.DESIGNERS_DEADLINE_DEFAULT}\033[0m')
    vk_token = next(
        (x for x in settings_list if x.key == 'vk_token'), None)
    if not vk_token:
        logger.error(
            "\033[93mТокен ВК не установлен\033[0m")
    await session.commit()
