import uuid
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from db.session import Base


class Image(Base):
    __tablename__ = 'images'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
