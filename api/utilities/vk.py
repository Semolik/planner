import asyncio
import datetime
import uuid
import json
from typing import Optional
from sqlalchemy import select
from vkbottle import (
    Bot,
    GroupEventType,
    Keyboard,
    Callback,
)
from vkbottle.bot import MessageEvent
from vkbottle.tools import WaiterMachine
from gigachat import GigaChat, Chat as GigaChatMessage, Messages, MessagesRole
from api.utilities.events import build_message
from api.schemas.vk import Chat
from api.cruds.vk_crud import VKCRUD
from api.cruds.settings_crud import SettingsCRUD
from api.cruds.events_crud import EventsCRUD
from api.cruds.tasks_crud import TasksCRUD
from api.models.user_models import User, UserRole
from api.models.app_models import AppSettings
from api.db.session import AsyncSession
from fastapi.logger import logger

from vkbottle.dispatch.rules.base import PeerRule

waiter = WaiterMachine()


class VKUtils:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.bot_task = None
        self.bot: Optional[Bot] = None
        self.wm = WaiterMachine()
        self.chat_fetch_cache = {}
        self.superusers_vk_ids = []
        # Состояние редактирования: {(user_id, peer_id): {"field": str, "event_data": dict}}
        self.editing_state = {}

    async def get_token(self):
        query = select(AppSettings)
        result = await self.session.execute(query)
        settings_list = result.scalars().all()
        token_setting = next((x for x in settings_list if x.key == "vk_token"), None)
        if not token_setting:
            return None
        return token_setting.value

    async def get_superusers_vk_ids(self):
        query = select(User.vk_id).where(User.is_superuser, User.vk_id.is_not(None))
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
                return Chat.model_validate(cached_chat["chat"])

        chat = await VKCRUD(self.session).get_chat_by_id(peer_id)
        if not chat:
            return None
        if not self.bot:
            return Chat.model_validate(chat)
        chat_info = await self.bot.api.messages.get_conversations_by_id(
            peer_ids=[peer_id],
            extended=False,
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

    def _build_event_info_message(self, event_data: dict) -> str:
        """Строит сообщение с информацией о событии"""
        result_message = f"📋 Информация о событии:\n\n"
        result_message += f"📅 Дата: {event_data.get('date', 'не указана')}\n"

        time_info = event_data.get('time', 'не указано')
        end_time = event_data.get('end_time')
        if end_time:
            time_info += f" - {end_time}"
        result_message += f"⏰ Время: {time_info}\n"

        location = event_data.get('location')
        location_str = location if location else "не указано"
        result_message += f"📍 Место: {location_str}\n"
        result_message += f"🎯 Название: {event_data.get('title', 'не указано')}\n"
        result_message += f"📊 Уровень: {event_data.get('level', 'не указан')}\n\n"

        return result_message

    def _build_event_edit_keyboard(self, event_data: dict) -> Keyboard:
        """Строит клавиатуру для редактирования полей события"""
        keyboard = Keyboard(one_time=False, inline=True)
        keyboard.add(
            Callback(
                "✏️ Название",
                payload={
                    "action": "edit_title",
                    "event_data": json.dumps(event_data, ensure_ascii=False),
                },
            )
        )
        keyboard.add(
            Callback(
                "✏️ Дата",
                payload={
                    "action": "edit_date",
                    "event_data": json.dumps(event_data, ensure_ascii=False),
                },
            )
        )
        keyboard.row()
        keyboard.add(
            Callback(
                "✏️ Время",
                payload={
                    "action": "edit_time",
                    "event_data": json.dumps(event_data, ensure_ascii=False),
                },
            )
        )
        keyboard.add(
            Callback(
                "✏️ Конец",
                payload={
                    "action": "edit_end_time",
                    "event_data": json.dumps(event_data, ensure_ascii=False),
                },
            )
        )
        keyboard.row()
        keyboard.add(
            Callback(
                "✏️ Место",
                payload={
                    "action": "edit_location",
                    "event_data": json.dumps(event_data, ensure_ascii=False),
                },
            )
        )
        keyboard.add(
            Callback(
                "✏️ Уровень",
                payload={
                    "action": "edit_level",
                    "event_data": json.dumps(event_data, ensure_ascii=False),
                },
            )
        )
        keyboard.row()
        keyboard.add(
            Callback(
                "✅ Добавить в систему",
                payload={
                    "action": "add_event",
                    "event_data": json.dumps(event_data, ensure_ascii=False),
                },
            )
        )
        return keyboard

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

        @bot.on.message(PeerRule(from_chat=False))
        async def handle_private_message(message):
            if message.from_id not in self.superusers_vk_ids:
                return

            user_id = message.from_id
            peer_id = message.peer_id
            state_key = (user_id, peer_id)

            # Проверяем, находимся ли в режиме редактирования
            if state_key in self.editing_state:
                edit_info = self.editing_state[state_key]
                field = edit_info["field"]
                event_data = edit_info["event_data"]
                event_message_id = edit_info.get("event_message_id")  # ID сообщения с информацией о событии

                new_value = message.text.strip()

                # Если field == "event_info_message", пользователь отправил новое сообщение
                # Очищаем состояние и обрабатываем это сообщение как новое
                if field == "event_info_message":
                    logger.info(f"Пользователь {user_id} отправил новое сообщение после обработки предыдущего события")
                    del self.editing_state[state_key]
                    # Показываем кнопки с действиями для нового сообщения
                    keyboard = Keyboard(one_time=False, inline=True)
                    keyboard.add(
                        Callback(
                            "✅ Обработать",
                            payload={
                                "action": "process_announcement",
                                "msg_id": message.conversation_message_id,
                            },
                        )
                    )
                    keyboard.row()
                    keyboard.add(
                        Callback(
                            "❌ Отклонить",
                            payload={
                                "action": "delete",
                                "msg_id": message.conversation_message_id,
                            },
                        )
                    )

                    await message.answer("Что сделать с этим сообщением?", keyboard=keyboard)
                    return

                if field == "title":
                    if not new_value:

                        await message.answer("❌ Название не может быть пустым")
                        return
                    event_data["title"] = new_value

                elif field == "date":
                    if not new_value or len(new_value.split(".")) != 3:
                        await message.answer(
                            "❌ Неверный формат даты. Используйте дд.мм.гггг"
                        )
                        return
                    event_data["date"] = new_value

                elif field == "time":
                    if not new_value or len(new_value.split(":")) != 2:
                        await message.answer(
                            "❌ Неверный формат времени. Используйте ЧЧ:ММ"
                        )
                        return
                    event_data["time"] = new_value

                elif field == "end_time":
                    if not new_value or len(new_value.split(":")) != 2:
                        await message.answer(
                            "❌ Неверный формат времени. Используйте ЧЧ:ММ"
                        )
                        return
                    event_data["end_time"] = new_value

                elif field == "location":
                    if not new_value:
                        await message.answer("❌ Место не может быть пустым")
                        return
                    event_data["location"] = new_value

                del self.editing_state[state_key]

                # Строим обновленное сообщение
                result_message = self._build_event_info_message(event_data)
                keyboard = self._build_event_edit_keyboard(event_data)

                # Редактируем старое сообщение вместо отправки нового
                try:
                    await bot.api.messages.edit(
                        peer_id=peer_id,
                        conversation_message_id=event_message_id,
                        message=result_message,
                        keyboard=keyboard.get_json(),
                    )
                except Exception as e:
                    logger.warning(f"Could not edit message: {e}. Sending new message instead.")
                    await message.answer(
                        result_message,
                        keyboard=keyboard.get_json(),
                    )

                # Сохраняем информацию о сообщении для последующего редактирования
                self.editing_state[state_key] = {
                    "field": "event_info_message",
                    "event_data": event_data,
                    "event_message_id": event_message_id,
                }

                logger.info(f"Поле {field} отредактировано пользователем {user_id}")
                return

            # Обычное сообщение - показываем кнопки с действиями
            keyboard = Keyboard(one_time=False, inline=True)
            keyboard.add(
                Callback(
                    "✅ Обработать",
                    payload={
                        "action": "process_announcement",
                        "msg_id": message.conversation_message_id,
                    },
                )
            )
            keyboard.row()
            keyboard.add(
                Callback(
                    "❌ Отклонить",
                    payload={
                        "action": "delete",
                        "msg_id": message.conversation_message_id,
                    },
                )
            )

            await message.answer("Что сделать с этим сообщением?", keyboard=keyboard)

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

        @bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
        async def handle_message_event(event: MessageEvent):
            user_id = event.user_id
            peer_id = event.peer_id
            message_id = event.conversation_message_id

            if user_id not in self.superusers_vk_ids:
                await event.show_snackbar("Вы не являетесь администратором!")
                return

            payload = event.payload
            action = payload.get("action")
            msg_id = payload.get("msg_id")

            if action == "process_announcement":
                try:
                    settings_crud = SettingsCRUD(self.session)
                    gigachat_token = await settings_crud.get_setting("gigachat_token")

                    if not gigachat_token:
                        await event.show_snackbar("⚠️ GigaChat токен не настроен")
                        logger.warning("GigaChat token not configured")
                        return

                    try:
                        response = (
                            await bot.api.messages.get_by_conversation_message_id(
                                conversation_message_ids=[msg_id],
                                peer_id=peer_id,
                            )
                        )

                        if not response.items:
                            await event.show_snackbar("Не удалось получить сообщение")
                            return

                        target_message = response.items[0]
                    except Exception as e:
                        logger.error(
                            f"Error getting message by conversation_message_id: {e}"
                        )
                        await event.show_snackbar("Не удалось получить сообщение")
                        return

                    original_message = None

                    if target_message.text:
                        original_message = target_message.text
                    elif (
                        target_message.fwd_messages
                        and len(target_message.fwd_messages) > 0
                    ):
                        fwd_texts = []
                        for fwd_msg in target_message.fwd_messages:
                            if fwd_msg.text:
                                # Форматируем дату и время сообщения
                                msg_date = ""
                                if hasattr(fwd_msg, 'date') and fwd_msg.date:
                                    msg_datetime = datetime.datetime.fromtimestamp(fwd_msg.date)
                                    msg_date = msg_datetime.strftime("%d.%m.%Y %H:%M")

                                # Определяем автора сообщения
                                author = "Организатор мероприятия"
                                if hasattr(fwd_msg, 'from_id') and fwd_msg.from_id == user_id:
                                    author = "Администратор системы"

                                # Собираем полное сообщение с подписью
                                message_with_signature = f"[{author}]"
                                if msg_date:
                                    message_with_signature += f" {msg_date}"
                                message_with_signature += f":\n{fwd_msg.text}"

                                fwd_texts.append(message_with_signature)

                        if fwd_texts:
                            original_message = "\n\n---\n\n".join(fwd_texts)

                    if not original_message:
                        await event.show_snackbar("Не удалось найти текст сообщения")
                        return

                    giga = GigaChat(
                        credentials=gigachat_token.value,
                        scope="GIGACHAT_API_PERS",
                        model="GigaChat",
                        verify_ssl_certs=False,
                    )

                    # Получаем все доступные уровни мероприятий
                    event_levels = await EventsCRUD(self.session).get_event_levels()

                    # Получаем default level из настроек
                    settings = await SettingsCRUD(self.session).get_settings()
                    default_level_id = settings.default_event_level_id
                    default_level = next((level for level in event_levels if level.id == default_level_id), None)

                    levels_list = ", ".join([level.name for level in event_levels]) if event_levels else "уровни не найдены"
                    default_level_name = default_level.name if default_level else "уровень по умолчанию"

                    current_date = datetime.datetime.now().strftime("%d.%m.%Y")
                    system_prompt = f"""Ты – виртуальный помощник по извлечению информации о событиях из текста. Твоя основная задача – извлекать следующую информацию о событии:

- `date`: дата начала проведения в формате dd.mm.yyyy
- `time`: время начала мероприятия в формате HH:MM (ВАЖНО: если мероприятие состоит из нескольких частей или проходит несколько дней, всегда бери САМОЕ РАННЕЕ время начала)
- `end_time`: время окончания мероприятия в формате HH:MM (если указано в тексте, если нет - оставь null)
- `location`: место проведения (ВАЖНО: если место НЕ упомянуто в тексте - оставь null)
- `title`: название мероприятия - может быть строка ИЛИ массив вариантов, если название неоднозначно (ВАЖНО: пиши официально, убирая вводные слова типа "мероприятие к", "события по", "праздник" и оставляя только суть названия)
- `level`: уровень мероприятия из списка: {levels_list}

Текущая дата: {current_date}

ВАЖНЫЕ ПРАВИЛА:
1. Если мероприятие проходит несколько дней, используй дату первого дня в поле `date`
2. Если указаны несколько времён начала (например, разные сессии или дни), берись САМОЕ РАННЕЕ время для `time`
3. Если указаны несколько времён окончания, бери САМОЕ ПОЗДНЕЕ время для `end_time`
4. Поле `end_time` может быть null, если время окончания не указано
5. Поле `location` (место) может быть null, если место не упомянуто в тексте. ВАЖНО: только если в тексте явно указано конкретное место - заполни это поле
6. НАЗВАНИЕ СОБЫТИЯ должно быть официальным и лаконичным:
   - УБИРАЙ вводные слова: "мероприятие к", "события по", "праздник", "фестиваль посвящённый", "день" и т.д.
   - ОСТАВЛЯЙ суть: вместо "Мероприятие к Дню студента" пиши "День студента", вместо "События по экологии" пиши "Экология"
   - Первое слово в названии должно быть с большой буквы
   - НЕОДНОЗНАЧНОСТЬ: Если название сильно неясно или может быть интерпретировано несколькими способами (например "Профориентационное мероприятие ИНГЕО"):
     * Верни МАССИВ вариантов вместо одной строки
     * Первый вариант - самый очевидный/явный из текста
     * Последующие варианты - альтернативные интерпретации
     * Минимум 2, максимум 4 варианта
   - Если название ясно - верни одну строку, не массив
7. ПРАВИЛА для поля `level` (уровень мероприятия):
   - ОСНОВНОЕ ПРАВИЛО: Если в тексте сообщения НЕ упомянут конкретный уровень из списка - ВСЕГДА используй уровень по умолчанию: "{default_level_name}"
   - ИСКЛЮЧЕНИЕ: Если в названии или описании явно упомянут один из доступных уровней - используй его
   - НЕ ГАДАЙ и НЕ ПРЕДПОЛАГАЙ уровень - если уровень не указан, используй уровень по умолчанию
   - Уровень ДОЛЖЕН быть ТОЛЬКО ИЗ ПРЕДОСТАВЛЕННОГО СПИСКА: {levels_list}
   - ВАЖНО: Уровень по умолчанию ВСЕГДА применяется, когда он явно не упомянут в тексте

Ответ должен содержать только корректно сформированный JSON-объект без пояснений или дополнительных комментариев.

Формат ответа:
```json
{{
  "date": "DD.MM.YYYY",
  "time": "HH:MM",
  "end_time": "HH:MM или null",
  "location": "Название места или null",
  "title": "Официальное название события",
  "level": "Один из доступных уровней (по умолчанию: {default_level_name})"
}}
```

ПРИМЕРЫ:
- Поле location: 
  * Если текст: "завтра финал баскетбола женского с 17:00-18:00" → location: null (место не упомянуто)
  * Если текст: "финал в спортивном зале" → location: "Спортивный зал"
- Поле level:
  * Если уровень не упомянут → ВСЕГДА используй "{default_level_name}"
  * Если текст: "городской уровень" → level: "Городской"
  * Если текст: просто событие без указания уровня → level: "{default_level_name}"
- Поле title:
  * Если ясно: "День студента" (строка)
  * Если неоднозначно: ["Профориентационное мероприятие ИНГЕО", "Профориентационная встреча института географии"] (массив вариантов)"""

                    # Логируем приходящее сообщение
                    logger.info(f"=== Анализ объявления ===")
                    logger.info(f"[Организатор мероприятия → Администратор системы]")
                    logger.info(f"Сообщение:\n{original_message}")

                    response = giga.chat(
                        payload=GigaChatMessage(
                            messages=[
                                Messages(
                                    role=MessagesRole.SYSTEM, content=system_prompt
                                ),
                                Messages(
                                    role=MessagesRole.USER, content=original_message
                                ),
                            ]
                        )
                    )

                    response_text = response.choices[0].message.content

                    # Логируем ответ GigaChat
                    logger.info(f"\n[Администратор системы → Результат обработки]")
                    logger.info(f"Ответ GigaChat:\n{response_text}")

                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1

                    if json_start != -1 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        event_data = json.loads(json_str)

                        # Обработка title: если это массив вариантов, сохраняем их и используем первый
                        title_variants = None
                        title_to_display = event_data.get('title', 'не указано')

                        if isinstance(title_to_display, list):
                            title_variants = title_to_display
                            title_to_display = title_variants[0]
                            event_data['title'] = title_to_display  # Сохраняем первый вариант в event_data

                        # Используем метод для построения сообщения
                        result_message = self._build_event_info_message(event_data)

                        # Используем метод для построения клавиатуры
                        keyboard = self._build_event_edit_keyboard(event_data)

                        # Отправляем сообщение и сохраняем его ID
                        response = await bot.api.messages.send(
                            peer_id=peer_id,
                            message=result_message,
                            keyboard=keyboard.get_json(),
                            random_id=0,
                        )
                        sent_message_id = response[0] if isinstance(response, list) else response

                        # Сохраняем информацию о сообщении в editing_state для последующего редактирования
                        self.editing_state[(user_id, peer_id)] = {
                            "field": "event_info_message",
                            "event_data": event_data,
                            "event_message_id": sent_message_id,
                        }

                        # Если есть варианты названия, показываем второе сообщение с выбором
                        if title_variants and len(title_variants) > 1:
                            variants_message = "📝 Выбери правильное название события:\n\n"
                            for i, variant in enumerate(title_variants, 1):
                                variants_message += f"{i}. {variant}\n"

                            variants_keyboard = Keyboard(one_time=False, inline=True)
                            for i, variant in enumerate(title_variants, 1):
                                variants_keyboard.add(
                                    Callback(
                                        f"{i}",
                                        payload={
                                            "action": "select_title_variant",
                                            "event_data": json.dumps(event_data, ensure_ascii=False),
                                            "variant_index": i - 1,
                                            "title_variants": json.dumps(title_variants, ensure_ascii=False),
                                        },
                                    )
                                )
                            variants_keyboard.row()
                            variants_keyboard.add(
                                Callback(
                                    "✅ Сохранить",
                                    payload={
                                        "action": "confirm_title_variant",
                                        "event_data": json.dumps(event_data, ensure_ascii=False),
                                    },
                                )
                            )

                            variants_response = await bot.api.messages.send(
                                peer_id=peer_id,
                                message=variants_message,
                                keyboard=variants_keyboard.get_json(),
                                random_id=0,
                            )
                            variants_message_id = variants_response[0] if isinstance(variants_response, list) else variants_response

                            # Сохраняем ID сообщения с вариантами названия
                            self.editing_state[(user_id, peer_id)] = {
                                "field": "title_variants_selection",
                                "event_data": event_data,
                                "event_message_id": sent_message_id,
                                "variants_message_id": variants_message_id,
                            }

                        await bot.api.messages.delete(
                            peer_id=peer_id,
                            conversation_message_ids=message_id,
                            delete_for_all=True,
                        )

                        logger.info(
                            f"Сообщение от пользователя {user_id} обработано как анонс. Данные: {event_data}"
                        )
                    else:
                        await event.show_snackbar(
                            "❌ Не удалось парсить ответ GigaChat"
                        )
                        logger.error(
                            f"Failed to parse GigaChat response: {response_text}"
                        )

                except Exception as e:
                    await event.show_snackbar(f"❌ Ошибка: {str(e)}")
                    logger.error(f"Error processing announcement: {str(e)}")

                return

            if action == "delete":
                await event.show_snackbar("Сообщение отклонено.")
                await bot.api.messages.delete(
                    peer_id=peer_id,
                    conversation_message_ids=message_id,
                    delete_for_all=True,
                )
                logger.info("Сообщение из личного диалога удалено.")
                return

            if action == "edit_title":
                event_data_str = payload.get("event_data")
                event_data = json.loads(event_data_str)
                self.editing_state[(user_id, peer_id)] = {
                    "field": "title",
                    "event_data": event_data,
                    "event_message_id": message_id,
                }
                await bot.api.messages.send(
                    peer_id=peer_id,
                    message="📝 Введите новое название мероприятия:",
                    random_id=0,
                )
                return

            if action == "edit_date":
                event_data_str = payload.get("event_data")
                event_data = json.loads(event_data_str)
                self.editing_state[(user_id, peer_id)] = {
                    "field": "date",
                    "event_data": event_data,
                    "event_message_id": message_id,
                }
                await bot.api.messages.send(
                    peer_id=peer_id,
                    message="📝 Введите новую дату (дд.мм.гггг):",
                    random_id=0,
                )
                return

            if action == "edit_time":
                event_data_str = payload.get("event_data")
                event_data = json.loads(event_data_str)
                self.editing_state[(user_id, peer_id)] = {
                    "field": "time",
                    "event_data": event_data,
                    "event_message_id": message_id,
                }
                await bot.api.messages.send(
                    peer_id=peer_id,
                    message="📝 Введите новое время (ЧЧ:ММ):",
                    random_id=0,
                )
                return

            if action == "edit_end_time":
                event_data_str = payload.get("event_data")
                event_data = json.loads(event_data_str)
                self.editing_state[(user_id, peer_id)] = {
                    "field": "end_time",
                    "event_data": event_data,
                    "event_message_id": message_id,
                }
                await bot.api.messages.send(
                    peer_id=peer_id,
                    message="📝 Введите время конца мероприятия (ЧЧ:ММ):",
                    random_id=0,
                )
                return

            if action == "edit_location":
                event_data_str = payload.get("event_data")
                event_data = json.loads(event_data_str)
                self.editing_state[(user_id, peer_id)] = {
                    "field": "location",
                    "event_data": event_data,
                    "event_message_id": message_id,
                }
                await bot.api.messages.send(
                    peer_id=peer_id,
                    message="📝 Введите новое место проведения:",
                    random_id=0,
                )
                return

            if action == "edit_level":
                event_data_str = payload.get("event_data")
                event_data = json.loads(event_data_str)

                # Получаем список уровней для выбора
                event_levels = await EventsCRUD(self.session).get_event_levels()

                # Сохраняем event_data в editing_state для использования при выборе уровня
                self.editing_state[(user_id, peer_id)] = {
                    "field": "level_selection",
                    "event_data": event_data,
                    "event_message_id": message_id,
                }

                # Создаем клавиатуру с кнопками уровней
                level_keyboard = Keyboard(one_time=False, inline=True)

                for i, level in enumerate(event_levels):
                    # Добавляем по 2 кнопки в ряд
                    if i > 0 and i % 2 == 0:
                        level_keyboard.row()

                    level_keyboard.add(
                        Callback(
                            level.name,
                            payload={
                                "action": "confirm_level",
                                "level_id": str(level.id),
                                "level_name": level.name,
                            },
                        )
                    )

                # Редактируем исходное сообщение со списком уровней
                await bot.api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=message_id,
                    message="Выберите уровень мероприятия:",
                    keyboard=level_keyboard.get_json(),
                )
                return

            if action == "select_title_variant":
                event_data_str = payload.get("event_data")
                event_data = json.loads(event_data_str)
                variant_index = int(payload.get("variant_index", 0))
                title_variants_str = payload.get("title_variants")
                title_variants = json.loads(title_variants_str)

                # Обновляем title на выбранный вариант
                selected_title = title_variants[variant_index]
                event_data["title"] = selected_title

                # Обновляем сообщение с выбранным вариантом
                variants_message = "📝 Выбранное название:\n\n"
                variants_message += f"✅ {selected_title}\n\n"
                variants_message += "Другие варианты:\n"

                for i, variant in enumerate(title_variants, 1):
                    if i - 1 != variant_index:
                        variants_message += f"{i}. {variant}\n"

                variants_keyboard = Keyboard(one_time=False, inline=True)
                for i, variant in enumerate(title_variants, 1):
                    variants_keyboard.add(
                        Callback(
                            f"{i}",
                            payload={
                                "action": "select_title_variant",
                                "event_data": json.dumps(event_data, ensure_ascii=False),
                                "variant_index": i - 1,
                                "title_variants": title_variants_str,
                            },
                        )
                    )
                variants_keyboard.row()
                variants_keyboard.add(
                    Callback(
                        "✅ Сохранить",
                        payload={
                            "action": "confirm_title_variant",
                            "event_data": json.dumps(event_data, ensure_ascii=False),
                        },
                    )
                )

                # Редактируем исходное сообщение со списком вариантов
                await bot.api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=message_id,
                    message=variants_message,
                    keyboard=variants_keyboard.get_json(),
                )
                return

            if action == "confirm_title_variant":
                event_data_str = payload.get("event_data")
                event_data = json.loads(event_data_str)
                state_key = (user_id, peer_id)

                # Получаем event_message_id из editing_state (основного сообщения с информацией о событии)
                event_message_id = None
                if state_key in self.editing_state:
                    event_message_id = self.editing_state[state_key].get("event_message_id")

                if not event_message_id:
                    await bot.api.messages.send(
                        peer_id=peer_id,
                        message="❌ Ошибка: не удалось найти сообщение события",
                        random_id=0,
                    )
                    return

                # Используем методы для построения сообщения и клавиатуры
                result_message = self._build_event_info_message(event_data)
                keyboard = self._build_event_edit_keyboard(event_data)

                # Редактируем исходное сообщение с информацией о событии
                await bot.api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=event_message_id,
                    message=result_message,
                    keyboard=keyboard.get_json(),
                )

                # Обновляем состояние
                self.editing_state[state_key] = {
                    "field": "event_info_message",
                    "event_data": event_data,
                    "event_message_id": event_message_id,
                }
                return

            if action == "confirm_level":
                level_name = payload.get("level_name")
                state_key = (user_id, peer_id)

                # Получаем event_data из editing_state
                if state_key not in self.editing_state or self.editing_state[state_key].get("field") != "level_selection":
                    await bot.api.messages.send(
                        peer_id=peer_id,
                        message="❌ Ошибка: данные события не найдены",
                        random_id=0,
                    )
                    return

                event_data = self.editing_state[state_key]["event_data"]
                event_message_id = self.editing_state[state_key].get("event_message_id")
                event_data["level"] = level_name

                # Отправляем обновленное сообщение с информацией о событии
                result_message = self._build_event_info_message(event_data)
                keyboard = self._build_event_edit_keyboard(event_data)

                # Редактируем исходное сообщение
                await bot.api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=event_message_id,
                    message=result_message,
                    keyboard=keyboard.get_json(),
                )

                # Обновляем состояние с новой информацией
                self.editing_state[state_key] = {
                    "field": "event_info_message",
                    "event_data": event_data,
                    "event_message_id": event_message_id,
                }
                return

            if action == "add_event":
                event_data_str = payload.get("event_data")
                event_data = json.loads(event_data_str)
                state_key = (user_id, peer_id)

                # Проверяем обязательные поля (location НЕ обязательное)
                required_fields = {
                    "title": "Название",
                    "date": "Дата",
                    "time": "Время начала",
                    "level": "Уровень"
                }

                missing_fields = []
                for field, display_name in required_fields.items():
                    if not event_data.get(field):
                        missing_fields.append(display_name)

                if missing_fields:
                    error_message = "❌ Не заполнены обязательные поля:\n"
                    for field in missing_fields:
                        error_message += f"• {field}\n"
                    error_message += "\nПожалуйста, заполните все поля перед добавлением."
                    await bot.api.messages.send(
                        peer_id=peer_id,
                        message=error_message,
                        random_id=0,
                    )
                    return

                try:
                    # Парсим дату
                    date_parts = event_data["date"].split(".")
                    event_date = datetime.datetime(
                        int(date_parts[2]), int(date_parts[1]), int(date_parts[0])
                    ).date()

                    # Парсим время начала
                    time_parts = event_data["time"].split(":")
                    start_time = datetime.time(int(time_parts[0]), int(time_parts[1]))

                    # Парсим или устанавливаем время окончания
                    if event_data.get("end_time"):
                        end_time_parts = event_data["end_time"].split(":")
                        end_time = datetime.time(int(end_time_parts[0]), int(end_time_parts[1]))
                    else:
                        # По умолчанию ставим время окончания на 2 часа позже начала
                        start_dt = datetime.datetime.combine(event_date, start_time)
                        end_dt = start_dt + datetime.timedelta(hours=2)
                        end_time = end_dt.time()
                        # Проверяем, не перейдет ли время в следующий день
                        if end_dt.date() != event_date:
                            # Если перейдет, ставим конец в 23:59 (или 23:00)
                            end_time = datetime.time(23, 0)

                    # Получаем level_id по названию уровня
                    event_levels = await EventsCRUD(self.session).get_event_levels()
                    level_id = None
                    for level in event_levels:
                        if level.name.lower() == event_data["level"].lower():
                            level_id = level.id
                            break

                    if not level_id:
                        await bot.api.messages.send(
                            peer_id=peer_id,
                            message=f"❌ Уровень '{event_data['level']}' не найден",
                            random_id=0,
                        )
                        await event.show_snackbar(f"❌ Уровень не найден")
                        return

                    # Проверяем, что место указано
                    if not event_data.get("location"):
                        await bot.api.messages.send(
                            peer_id=peer_id,
                            message="❌ Место проведения не указано. Пожалуйста, отредактируйте событие и добавьте место.",
                            random_id=0,
                        )
                        # Возвращаем в режим редактирования события
                        self.editing_state[state_key] = {
                            "field": "event_info_message",
                            "event_data": event_data,
                            "event_message_id": None,
                        }
                        await event.show_snackbar("⚠️ Место проведения не указано")
                        return

                    # Создаем событие в БД
                    new_event = await EventsCRUD(self.session).create_event(
                        name=event_data["title"],
                        date=event_date,
                        location=event_data["location"],
                        organizer="",
                        start_time=start_time,
                        end_time=end_time,
                        name_approved=True,
                        required_photographers=1,
                        description="",
                        level_id=level_id,
                    )

                    await self.session.commit()

                    # Получаем настройки для дедлайнов
                    settings = await SettingsCRUD(self.session).get_settings()

                    # Вычисляем дедлайны: дата мероприятия + значение из настроек (в днях)
                    photographers_deadline = new_event.date + datetime.timedelta(days=settings.photographers_deadline)
                    designers_deadline = new_event.date + datetime.timedelta(days=settings.designers_deadline)
                    copywriters_deadline = new_event.date + datetime.timedelta(days=settings.copywriters_deadline)

                    # Создаем основную задачу для мероприятия
                    task = await TasksCRUD(self.session).create_task(
                        name="Освещение мероприятия",
                        event_id=new_event.id,
                        use_in_pgas=True,
                    )

                    # Создаем типизированную задачу для фотографов
                    await TasksCRUD(self.session).create_typed_task(
                        task_id=task.id,
                        task_type=UserRole.PHOTOGRAPHER,
                        description="",
                        for_single_user=False,
                        due_date=photographers_deadline,
                    )

                    # Создаем типизированную задачу для дизайнеров
                    await TasksCRUD(self.session).create_typed_task(
                        task_id=task.id,
                        task_type=UserRole.DESIGNER,
                        description="",
                        for_single_user=True,
                        due_date=designers_deadline,
                    )

                    # Создаем типизированную задачу для копирайтеров
                    await TasksCRUD(self.session).create_typed_task(
                        task_id=task.id,
                        task_type=UserRole.COPYWRITER,
                        description="",
                        for_single_user=True,
                        due_date=copywriters_deadline,
                    )

                    await self.session.commit()

                    time_info = event_data.get('time', '')
                    actual_end_time = end_time.strftime("%H:%M")
                    time_info += f" - {actual_end_time}"

                    await bot.api.messages.send(
                        peer_id=peer_id,
                        message=f"✅ Событие успешно добавлено:\n\n📅 {event_data.get('date')}\n⏰ {time_info}\n📍 {event_data.get('location')}\n🎯 {event_data.get('title')}\n📊 {event_data.get('level')}",
                        random_id=0,
                    )

                    await event.show_snackbar("✅ Событие добавлено успешно")

                    await bot.api.messages.delete(
                        peer_id=peer_id,
                        conversation_message_ids=message_id,
                        delete_for_all=True,
                    )

                    # Очищаем состояние редактирования
                    state_key = (user_id, peer_id)
                    if state_key in self.editing_state:
                        del self.editing_state[state_key]

                    logger.info(f"Событие добавлено пользователем {user_id}: {event_data}, ID события: {new_event.id}")

                except ValueError as e:
                    await bot.api.messages.send(
                        peer_id=peer_id,
                        message=f"❌ Ошибка формата данных: {str(e)}",
                        random_id=0,
                    )
                    await event.show_snackbar("❌ Ошибка формата данных")
                    logger.error(f"Error parsing event data: {e}")
                except Exception as e:
                    await bot.api.messages.send(
                        peer_id=peer_id,
                        message=f"❌ Ошибка при добавлении события: {str(e)}",
                        random_id=0,
                    )
                    await event.show_snackbar("❌ Ошибка при добавлении события")
                    logger.error(f"Error adding event: {e}")

                return

            chat_type = payload.get("type")
            if not chat_type:
                return

            chat_type = chat_type.lower()

            if chat_type == "finish":
                await event.show_snackbar("Настройка завершена.")
                await bot.api.messages.delete(
                    peer_id=peer_id,
                    conversation_message_ids=message_id,
                    delete_for_all=True,
                )
                return

            chat_info = await bot.api.messages.get_conversations_by_id(
                peer_ids=[peer_id],
                extended=False,
            )
            if not chat_info or not chat_info.items:
                await event.show_snackbar(
                    "Боту необходимо выдать права администратора!"
                )
                return
            chat_role_map = {
                "фотографы": (UserRole.PHOTOGRAPHER, "фотографов"),
                "копирайтеры": (UserRole.COPYWRITER, "копирайтеров"),
                "дизайнеры": (UserRole.DESIGNER, "дизайнеров"),
            }

            if chat_type not in chat_role_map:
                await event.show_snackbar("Неизвестный тип чата.")
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
                peer_id=peer_id,
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
