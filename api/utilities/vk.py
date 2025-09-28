import asyncio
import datetime
import uuid
from sqlalchemy import select
from vkbottle import (
    Bot,
    GroupEventType,
    Keyboard,
    Callback,
    GroupTypes,
)
from vkbottle.tools import WaiterMachine
from utilities.events import build_message
from schemas.vk import Chat
from cruds.vk_crud import VKCRUD
from models.user_models import User, UserRole
from models.app_models import AppSettings
from db.session import AsyncSession
from fastapi.logger import logger

from vkbottle.dispatch.rules.base import PeerRule

waiter = WaiterMachine()


class VKUtils:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.bot_task = None
        self.bot: Bot = None
        self.wm = WaiterMachine()
        self.chat_fetch_cache = {}
        self.superusers_vk_ids = []

    async def get_token(self):
        query = select(AppSettings)
        result = await self.session.execute(query)
        settings_list = result.scalars().all()
        token_setting = next((x for x in settings_list if x.key == "vk_token"), None)
        if not token_setting:
            return None
        return token_setting.value

    async def get_superusers_vk_ids(self):
        query = select(User.vk_id).where(
            User.is_superuser == True, User.vk_id.is_not(None)
        )
        result = await self.session.execute(query)
        superusers_vk_ids = result.scalars().all()
        return superusers_vk_ids if superusers_vk_ids else []

    async def start_bot(self, token: str):
        if self.bot_task:
            logger.warning("VK bot is already running.")
            return
        try:
            loop = asyncio.get_event_loop()
            print("Starting VK bot...")
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

    def update_superusers_vk_ids(
        self, added_user_id: uuid.UUID = None, removed_user_id: uuid.UUID = None
    ):
        if added_user_id:
            if added_user_id not in self.superusers_vk_ids:
                self.superusers_vk_ids.append(added_user_id)
                logger.info(f"Added VK superuser ID: {added_user_id}")
        if removed_user_id:
            if removed_user_id in self.superusers_vk_ids:
                self.superusers_vk_ids.remove(removed_user_id)
                logger.info(f"Removed VK superuser ID: {removed_user_id}")

    async def get_chat_by_id(self, peer_id):
        if peer_id in self.chat_fetch_cache:
            cached_chat = self.chat_fetch_cache[peer_id]
            if (
                cached_chat["timestamp"] + (60 * 5)
                > datetime.datetime.now().timestamp()
            ):
                print(f"Using cached chat for peer_id {peer_id}")
                return Chat.model_validate(cached_chat["chat"])

        chat = await VKCRUD(self.session).get_chat_by_id(peer_id)
        if not chat:
            return None
        if not self.bot:
            return Chat.model_validate(chat)
        chat_info = await self.bot.api.messages.get_conversations_by_id(
            peer_ids=peer_id,
            extended=0,
        )
        chat = await VKCRUD(self.session).update_chat(
            chat,
            name=chat_info.items[0].chat_settings.title,
            members_count=chat_info.items[0].chat_settings.members_count,
            pin_message_id=chat.pin_message_id,
        )
        self.chat_fetch_cache[peer_id] = {
            "chat": Chat.model_validate(chat),
            "timestamp": datetime.datetime.now().timestamp(),
        }
        return self.chat_fetch_cache[peer_id]["chat"]

    async def update_messages(self):
        chats = await VKCRUD(self.session).get_all_chats()
        for chat in chats:
            message = await build_message(db=self.session, role=chat.chat_role)
            # edit pin message if it exists
            if chat.pin_message_id:
                try:
                    await self.bot.api.messages.edit(
                        peer_id=chat.chat_id,
                        message=message,
                        cmid=chat.pin_message_id,
                        dont_parse_links=True,
                    )
                except Exception as e:
                    logger.error(f"Error editing pin message: {e}")
            else:
                logger.info(
                    f"Pin message not found for chat {chat.chat_id}, sending new message."
                )

    def update_messages_task(self):
        if not self.bot_task:
            logger.warning("VK bot is not running. Cannot update messages.")
            return
        loop = asyncio.get_event_loop()
        self.bot_task = loop.create_task(self.update_messages())

    def add_bot_handlers(self, bot: Bot):
        @bot.on.message(text=["/ping"])
        async def start_handler(message):
            await message.answer("pong")

        @bot.on.message(PeerRule(from_chat=True), text=["/setup"])
        async def setup_handler(message, bot_id=None):
            if message.from_id not in self.superusers_vk_ids:
                await message.answer("У вас нет прав для выполнения этой команды.")
                return

            query = select(AppSettings).where(
                AppSettings.key.in_(
                    [
                        "vk_chat_photographers_enabled",
                        "vk_chat_copywriters_enabled",
                        "vk_chat_designers_enabled",
                    ]
                )
            )
            result = await self.session.execute(query)
            settings_list = result.scalars().all()
            enabled_chats = {s.key: s.value.lower() == "true" for s in settings_list}

            keyboard = Keyboard(one_time=False, inline=True)

            chat_options = []
            if enabled_chats.get("vk_chat_photographers_enabled"):
                chat_options.append("Фотографы")
            if enabled_chats.get("vk_chat_copywriters_enabled"):
                chat_options.append("Копирайтеры")
            if enabled_chats.get("vk_chat_designers_enabled"):
                chat_options.append("Дизайнеры")

            if not chat_options:
                await message.answer("Нет доступных чатов для настройки.")
                return

            for option in chat_options:
                keyboard.add(Callback(option, payload={"type": option.lower()}))

            keyboard.row()
            keyboard.add(Callback("Завершить", payload={"type": "finish"}))

            await message.answer("Выберите тип чата для настройки:", keyboard=keyboard)

        @bot.on.raw_event(
            GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent
        )
        async def handle_message_event(event: GroupTypes.MessageEvent):
            user_id = event.object.user_id
            peer_id = event.object.peer_id
            event_id = event.object.event_id

            message_id = event.object.conversation_message_id
            if user_id not in self.superusers_vk_ids:
                await bot.api.messages.send_message_event_answer(
                    event_id=event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data='{"type": "show_snackbar", "text": "Вы не являетесь администратором!"}',
                )
                return

            payload = event.object.payload
            chat_type = payload.get("type").lower()

            if chat_type == "finish":
                await bot.api.messages.send_message_event_answer(
                    event_id=event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data='{"type": "show_snackbar", "text": "Настройка завершена."}',
                )

                await bot.api.messages.delete(
                    peer_id=peer_id,
                    conversation_message_ids=message_id,
                    delete_for_all=True,
                )
                return
            chat_info = await bot.api.messages.get_conversations_by_id(
                peer_ids=peer_id,
                extended=0,
            )
            if not chat_info or not chat_info.items:
                await bot.api.messages.send_message_event_answer(
                    event_id=event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data='{"type": "show_snackbar", "text": "Боту необходимо выдать права администратора!"}',
                )
                return
            chat_role_map = {
                "фотографы": (UserRole.PHOTOGRAPHER, "фотографов"),
                "копирайтеры": (UserRole.COPYWRITER, "копирайтеров"),
                "дизайнеры": (UserRole.DESIGNER, "дизайнеров"),
            }

            if chat_type not in chat_role_map:
                await bot.api.messages.send_message_event_answer(
                    event_id=event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data='{"type": "show_snackbar", "text": "Неизвестный тип чата."}',
                )
                return

            chat_key, chat_title = chat_role_map[chat_type]
            chat = await VKCRUD(self.session).get_chat_by_id(peer_id)
            if chat and chat.chat_id == peer_id:
                await VKCRUD(self.session).delete(chat)
            chat = await VKCRUD(self.session).get_chat_by_role(chat_key)
            chat_name = chat_info.items[0].chat_settings.title
            if chat:
                await VKCRUD(self.session).delete(chat)
            chat = await VKCRUD(self.session).create_chat(
                chat_id=peer_id,
                chat_role=chat_key,
                name=chat_name,
                members_count=chat_info.items[0].chat_settings.members_count,
            )

            await bot.api.messages.send(
                peer_id=event.object.peer_id,
                message=f"Чат для {chat_title} установлен",
                random_id=0,
            )

            await bot.api.messages.delete(
                peer_id=peer_id,
                conversation_message_ids=message_id,
                delete_for_all=True,
            )

        @bot.on.message(PeerRule(from_chat=True), text=["/pin"])
        async def create_pin_message_handler(message):
            if message.from_id not in self.superusers_vk_ids:
                await message.answer("У вас нет прав для выполнения этой команды.")
                return
            vk_crud = VKCRUD(self.session)
            chat = await vk_crud.get_chat_by_id(message.peer_id)
            if not chat:
                return

            message_text = await build_message(self.session, role=chat.chat_role)

            msg = await message.answer(
                message_text,
            )
            await bot.api.messages.pin(
                peer_id=message.peer_id,
                conversation_message_id=msg.conversation_message_id,
            )
            await vk_crud.update_chat(
                chat,
                name=chat.name,
                members_count=chat.members_count,
                pin_message_id=msg.conversation_message_id,
            )
