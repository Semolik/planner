import asyncio
from sqlalchemy import select
from vkbottle import Bot
from models.app import AppSettings
from db.session import async_session_maker


class VKUtils:

    async def get_token():
        async with async_session_maker() as session:
            query = select(AppSettings)
            result = await session.execute(query)
            settings_list = result.scalars().all()
            token_setting = next(
                (x for x in settings_list if x.key == 'vk_token'), None)
            if not token_setting:
                raise ValueError("Токен не установлен")
            return token_setting.value

    async def start_bot(self, loop: asyncio.AbstractEventLoop):
        try:
            token = await self.get_token()
            print(f"Токен: {token}")
            bot = Bot(token=token)
            loop.create_task(bot.run_polling())
            return bot
        except Exception as e:
            print(f"Ошибка при запуске бота: {e}")
            return None
