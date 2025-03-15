import uuid
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Enum, String, DateTime, ForeignKey, Text, Boolean, UniqueConstraint, TIMESTAMP, select
from models.user import User, UserRole
from db.session import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    date = Column(type_=TIMESTAMP(timezone=True), nullable=False)
    location = Column(String, nullable=False)
    link = Column(String, nullable=True)
    organizer = Column(String, nullable=True)
    task = relationship("Task", back_populates="event", uselist=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey(
        'events.id'), nullable=True)
    due_date = Column(type_=TIMESTAMP(timezone=True), nullable=True)
    event = relationship(Event,
                         foreign_keys=[event_id])
    typed_tasks = relationship("TypedTask", back_populates="task")


class TaskState(Base):
    __tablename__ = "task_states"

    type_task_id = Column(UUID(as_uuid=True), ForeignKey(
        'typed_tasks.id'), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), primary_key=True)
    is_completed = Column(Boolean, nullable=False, default=False)
    comment = Column(Text, nullable=True)

    typed_task = relationship(
        "TypedTask",
        foreign_keys=[type_task_id],
        uselist=False,
        overlaps="users"  # Указываем, что это отношение перекрывается с users
    )
    user = relationship(
        "User",
        foreign_keys=[user_id],
        uselist=False,
        overlaps="users"  # Указываем, что это отношение перекрывается с users
    )


class TypedTask(Base):
    __tablename__ = "typed_tasks"
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey(
        'tasks.id'), nullable=False)
    task_type = Column(Enum(UserRole), nullable=False)
    description = Column(Text, nullable=True)
    for_single_user = Column(Boolean, nullable=False)
    __table_args__ = (
        UniqueConstraint('task_id', 'task_type',
                         name='uq_typed_task_task_id_task_type'),
    )

    task = relationship("Task", foreign_keys=[task_id], uselist=False)
    task_states = relationship("TaskState", back_populates="typed_task")
    users = relationship(
        "User",
        secondary="task_states",
        primaryjoin="TypedTask.id == TaskState.type_task_id",
        secondaryjoin="User.id == TaskState.user_id",
        overlaps="task_states"
    )
