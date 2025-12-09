import uuid
from sqlalchemy import Column, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from api.models.user_models import UserRole
from api.models.files_models import File
from sqlalchemy.orm import relationship
from api.db.session import Base


class HomeNote(Base):
    __tablename__ = "home_notes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False, default="")
    role = Column(Enum(UserRole), nullable=False)
    files = relationship(
        File, secondary="home_files", overlaps="home_files", viewonly=True
    )


class HomeFile(Base):
    __tablename__ = "home_files"
    home_note_id = Column(
        UUID(as_uuid=True),
        ForeignKey(HomeNote.id, ondelete="CASCADE"),
        primary_key=True,
    )
    file_id = Column(
        UUID(as_uuid=True), ForeignKey(File.id, ondelete="CASCADE"), primary_key=True
    )
    file = relationship(
        File,
        foreign_keys=[file_id],
        uselist=False,
        overlaps="task_files",
        cascade="all, delete-orphan",
        single_parent=True,
    )
