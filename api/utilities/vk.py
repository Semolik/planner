import asyncio
from sqlalchemy import select
from vkbottle import Bot, Keyboard, Text, EMPTY_KEYBOARD
from vkbottle.tools import WaiterMachine
from models.user_models import User
from models.app_models import AppSettings
from db.session import AsyncSession
from fastapi.logger import logger
from vkbottle import PayloadRule, Message, Keyboard, ButtonColor, EMPTY_KEYBOARD
from vkbottle.dispatch.rules.base import PeerRule

from vkbottle.dispatch.rules.base import PeerRule

waiter = WaiterMachine()


class VKUtils:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.bot_task = None
        self.bot: Bot = None
        self.wm = WaiterMachine()

    async def get_token(self):
        query = select(AppSettings)
        result = await self.session.execute(query)
        settings_list = result.scalars().all()
        token_setting = next(
            (x for x in settings_list if x.key == 'vk_token'), None)
        if not token_setting:
            return None
        return token_setting.value

    async def get_superusers_vk_ids(self):
        query = select(User.vk_id).where(
            User.is_superuser == True, User.vk_id.is_not(None))
        result = await self.session.execute(query)
        superusers_vk_ids = result.scalars().all()
        return superusers_vk_ids if superusers_vk_ids else []

    async def start_bot(self, token: str):
        if self.bot_task:
            logger.warning("VK bot is already running.")
            return
        try:
            loop = asyncio.get_event_loop()
            bot = Bot(token=token)
            self.bot_task = loop.create_task(bot.run_polling())
            self.superusers_vk_ids = await self.get_superusers_vk_ids()
            self.bot = bot
            self.add_bot_handlers(bot)
        except Exception as e:
            print(f"Error starting VK bot: {e}")
            return None

    async def stop_bot(self):
        if self.bot_task:
            self.bot._polling.stop = True
            self.bot_task.cancel()

            try:
                await self.bot_task
            except Exception as e:
                print(f"Error stopping VK bot: {e}")

            self.bot_task = None
            self.bot = None
            print("VK bot stopped successfully.")
        else:
            print("No VK bot task to stop.")

    def add_bot_handlers(self, bot: Bot):
        @bot.on.message(text="/start")
        async def start_handler(message: Message):
            await message.answer("VK bot is running!")
            logger.info("VK bot started successfully.")

        @bot.on.message(PeerRule(from_chat=True), text="/setup")
        async def setup_handler(message: Message):
            if message.from_id not in self.superusers_vk_ids:
                await message.answer("У вас нет прав для выполнения этой команды.")
                return

            # Получаем статусы включенных чатов
            query = select(AppSettings).where(
                AppSettings.key.in_([
                    "vk_chat_photographers_enabled",
                    "vk_chat_copywriters_enabled",
                    "vk_chat_designers_enabled"
                ])
            )
            result = await self.session.execute(query)
            settings_list = result.scalars().all()
            enabled_chats = {
                s.key: s.value.lower() == 'true' for s in settings_list
            }

            # Формируем inline-клавиатуру только для включённых чатов
            keyboard = Keyboard(inline=True)

            chat_options = []
            if enabled_chats.get("vk_chat_photographers_enabled"):
                chat_options.append(("Фотографы", "photographers"))
            if enabled_chats.get("vk_chat_copywriters_enabled"):
                chat_options.append(("Копирайтеры", "copywriters"))
            if enabled_chats.get("vk_chat_designers_enabled"):
                chat_options.append(("Дизайнеры", "designers"))

            if not chat_options:
                await message.answer("Нет доступных чатов для настройки.")
                return

            for label, role in chat_options:
                keyboard.add(
                    Text(label, {"type": "chat_type", "role": role}), color=ButtonColor.PRIMARY)
                keyboard.row()

            keyboard.add(
                Text("Завершить", {"type": "action", "value": "finish"}))

            await message.answer("Выберите тип чата для настройки:", keyboard=keyboard)

        # Обработка выбора через payload
        @bot.on.message(PayloadRule({"type": "chat_type"}))
        async def handle_chat_type(message: Message):
            payload = message.payload
            role = payload.get("role")

            chat_role_map = {
                "photographers": ("photographers", "фотографов"),
                "copywriters": ("copywriters", "копирайтеров"),
                "designers": ("designers", "дизайнеров")
            }

            if role not in dict(chat_role_map):
                await message.answer("Неизвестный тип чата.")
                return

            _, chat_title = chat_role_map[role]

            # Сохраняем peer_id текущего чата
            chat_id = message.peer_id
            setting_key = f"vk_chat_{role}_id"

            query = select(AppSettings).where(AppSettings.key == setting_key)
            result = await self.session.execute(query)
            chat_setting = result.scalar_one_or_none()

            if chat_setting:
                chat_setting.value = str(chat_id)
            else:
                chat_setting = AppSettings(key=setting_key, value=str(chat_id))
                self.session.add(chat_setting)

            await self.session.commit()
            await message.answer(f"Чат для {chat_title} успешно установлен!")

        # Обработка завершения
        @bot.on.message(PayloadRule({"type": "action", "value": "finish"}))
        async def finish_handler(message: Message):
            await message.answer("Настройка завершена.", keyboard=EMPTY_KEYBOARD)
