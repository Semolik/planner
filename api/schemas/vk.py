from pydantic import BaseModel
from uuid import UUID

from models.user_models import UserRole


class Chat(BaseModel):
    id: UUID
    name: str
    chat_id: int
    chat_role: UserRole
    members_count: int

    class Config:
        from_attributes = True


class UpdateChatSettings(BaseModel):
    vk_chat_photographers_enabled: bool
    vk_chat_copywriters_enabled: bool
    vk_chat_designers_enabled: bool


class ChatsSettingsResponse(UpdateChatSettings):
    photographers_chat: Chat | None
    copywriters_chat: Chat | None
    designers_chat: Chat | None
    vk_token_set: bool

    class Config:
        from_attributes = True
