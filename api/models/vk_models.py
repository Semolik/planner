import uuid
from sqlalchemy import UUID, Column, Integer
from db.session import Base


class Chat(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(Integer, nullable=False)
    pin_message_id = Column(Integer, nullable=False)
