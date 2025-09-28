from sqlalchemy import select


from schemas.vk import ChatsSettingsResponse
from models.user_models import UserRole
from cruds.base_crud import BaseCRUD
from models.vk_models import Chat
from models.app_models import AppSettings


class VKCRUD(BaseCRUD):
    async def create_chat(
        self, chat_id: int, chat_role: UserRole, name: str, members_count: int
    ):
        chat = Chat(
            chat_id=chat_id, chat_role=chat_role, name=name, members_count=members_count
        )
        await self.create(chat)

    async def get_all_chats(self) -> list[Chat]:
        query = select(Chat)
        result = await self.db.execute(query)
        chats = result.scalars().all()
        return chats

    async def get_chat_by_role(self, chat_role: UserRole) -> Chat:
        query = select(Chat).where(Chat.chat_role == chat_role)
        result = await self.db.execute(query)
        chat = result.scalars().first()
        return chat

    async def get_chat_by_id(self, chat_id: int) -> Chat:
        query = select(Chat).where(Chat.chat_id == chat_id)
        result = await self.db.execute(query)
        chat = result.scalars().first()
        return chat

    async def update_chat(
        self,
        chat: Chat,
        name: str,
        members_count: int,
        pin_message_id: int | None = None,
    ):
        chat.name = name
        chat.pin_message_id = pin_message_id
        chat.members_count = members_count
        return await self.update(chat)

    async def get_chats_settings(self, vk_utils) -> ChatsSettingsResponse:
        photographers_enabled_query = (
            select(AppSettings.value)
            .where(AppSettings.key == "vk_chat_photographers_enabled")
            .limit(1)
        )
        copywriters_enabled_query = (
            select(AppSettings.value)
            .where(AppSettings.key == "vk_chat_copywriters_enabled")
            .limit(1)
        )
        designers_enabled_query = (
            select(AppSettings.value)
            .where(AppSettings.key == "vk_chat_designers_enabled")
            .limit(1)
        )
        token_query = (
            select(AppSettings.value).where(AppSettings.key == "vk_token").limit(1)
        )

        # Get chats
        photographer_chat_query = select(Chat).where(
            Chat.chat_role == UserRole.PHOTOGRAPHER
        )
        copywriter_chat_query = select(Chat).where(
            Chat.chat_role == UserRole.COPYWRITER
        )
        designer_chat_query = select(Chat).where(Chat.chat_role == UserRole.DESIGNER)

        # Execute queries
        photographers_enabled_result = await self.db.execute(
            photographers_enabled_query
        )
        copywriters_enabled_result = await self.db.execute(copywriters_enabled_query)
        designers_enabled_result = await self.db.execute(designers_enabled_query)
        token_result = await self.db.execute(token_query)

        photographer_chat_result = await self.db.execute(photographer_chat_query)
        copywriter_chat_result = await self.db.execute(copywriter_chat_query)
        designer_chat_result = await self.db.execute(designer_chat_query)

        # Get values
        photographers_enabled_value = photographers_enabled_result.scalar()
        copywriters_enabled_value = copywriters_enabled_result.scalar()
        designers_enabled_value = designers_enabled_result.scalar()
        token_value = token_result.scalar()

        photographer_chat = photographer_chat_result.scalars().first()
        copywriter_chat = copywriter_chat_result.scalars().first()
        designer_chat = designer_chat_result.scalars().first()

        photographers_enabled = (
            bool(photographers_enabled_value == "true")
            if photographers_enabled_value
            else False
        )
        copywriters_enabled = (
            bool(copywriters_enabled_value == "true")
            if copywriters_enabled_value
            else False
        )
        designers_enabled = (
            bool(designers_enabled_value == "true")
            if designers_enabled_value
            else False
        )
        token_set = bool(token_value) if token_value else False

        return ChatsSettingsResponse(
            vk_chat_photographers_enabled=photographers_enabled,
            vk_chat_copywriters_enabled=copywriters_enabled,
            vk_chat_designers_enabled=designers_enabled,
            photographers_chat=(
                await vk_utils.get_chat_by_id(photographer_chat.chat_id)
                if photographer_chat
                else None
            ),
            copywriters_chat=(
                await vk_utils.get_chat_by_id(copywriter_chat.chat_id)
                if copywriter_chat
                else None
            ),
            designers_chat=(
                await vk_utils.get_chat_by_id(designer_chat.chat_id)
                if designer_chat
                else None
            ),
            vk_token_set=token_set,
        )
