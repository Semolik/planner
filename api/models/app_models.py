import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from api.db.session import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, nullable=False, unique=True)
    value = Column(Text, nullable=False)
