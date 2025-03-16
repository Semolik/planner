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
    date = Column(TIMESTAMP(timezone=True), nullable=False)
    location = Column(String, nullable=False)
    organizer = Column(String, nullable=True)
    link = Column(Text, nullable=True)

    # Cascade deletion for Task
    task = relationship(
        "Task",
        uselist=False,
        back_populates="event",
        cascade="all, delete-orphan",
        single_parent=True
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey('events.id', ondelete='CASCADE'),  # Ensure CASCADE here
        nullable=True
    )
    due_date = Column(TIMESTAMP(timezone=True), nullable=True)

    event = relationship(
        "Event",
        foreign_keys=[event_id],
        uselist=False,
        back_populates="task",
        cascade="all, delete-orphan",
        single_parent=True
    )

    typed_tasks = relationship(
        "TypedTask",
        back_populates="parent_task",
        cascade="all, delete-orphan",
        single_parent=True
    )


class TypedTask(Base):
    __tablename__ = "typed_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey('tasks.id', ondelete='CASCADE'),  # Ensure CASCADE here
        nullable=False
    )
    task_type = Column(Enum(UserRole), nullable=False)
    description = Column(Text, nullable=True)
    for_single_user = Column(Boolean, nullable=False)
    link = Column(Text, nullable=True)
    __table_args__ = (
        UniqueConstraint('task_id', 'task_type',
                         name='uq_typed_task_task_id_task_type'),
    )

    parent_task = relationship(
        "Task",
        foreign_keys=[task_id],
        uselist=False,
        back_populates="typed_tasks",
        cascade="all, delete-orphan",
        single_parent=True
    )

    task_states = relationship(
        "TaskState",
        back_populates="typed_task",
        cascade="all, delete-orphan"
    )

    users = relationship(
        "User",
        secondary="task_states",
        primaryjoin="TypedTask.id == TaskState.type_task_id",
        secondaryjoin="User.id == TaskState.user_id",
        overlaps="task_states"
    )


class TaskState(Base):
    __tablename__ = "task_states"

    type_task_id = Column(
        UUID(as_uuid=True),
        # Ensure CASCADE here
        ForeignKey('typed_tasks.id', ondelete='CASCADE'),
        primary_key=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),  # Ensure CASCADE here
        primary_key=True
    )
    is_completed = Column(Boolean, nullable=False, default=False)
    comment = Column(Text, nullable=True)

    typed_task = relationship(
        "TypedTask",
        foreign_keys=[type_task_id],
        uselist=False,
        overlaps="users",
        cascade="all, delete-orphan",
        single_parent=True
    )
    user = relationship(
        "User",
        foreign_keys=[user_id],
        uselist=False,
        overlaps="users",
        cascade="all, delete-orphan",
        single_parent=True
    )
