import uuid
from sqlalchemy import UUID, Column, Enum, Integer, String
from models.user_models import UserRole
from db.session import Base


class Chat(Base):
    __tablename__ = "chats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    chat_id = Column(Integer, nullable=False)
    pin_message_id = Column(Integer, nullable=True)
    chat_role = Column(Enum(UserRole), primary_key=True)
    members_count = Column(Integer, nullable=False, default=0)
