import uuid
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Enum, String, DateTime, ForeignKey, Text, Boolean, UniqueConstraint, TIMESTAMP, select
from sqlalchemy.sql import func
from models.user import User, UserRole
from db.session import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    date = Column(TIMESTAMP(timezone=True), nullable=False)
    location = Column(String, nullable=False)
    organizer = Column(String, nullable=False, default="")
    link = Column(Text, nullable=False, default="")

    # Внешний ключ на EventGroup (событие принадлежит одной группе)
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey('event_groups.id', ondelete='SET NULL'),
        nullable=True
    )

    # Связь с EventGroup
    group = relationship(
        "EventGroup",
        foreign_keys=[group_id],
        back_populates="events"
    )

    # Cascade deletion for Task
    task = relationship(
        "Task",
        uselist=False,
        back_populates="event",
        cascade="all, delete-orphan",
        single_parent=True
    )


class EventGroup(Base):
    __tablename__ = "event_groups"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False, default="")
    organizer = Column(String, nullable=False, default="")
    link = Column(Text, nullable=False, default="")
    events = relationship(
        "Event",
        primaryjoin="EventGroup.id == EventGroupAssociation.group_id",
        secondary="event_group_associations",
        back_populates="group"
    )


class EventGroupAssociation(Base):
    __tablename__ = "event_group_associations"

    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey('events.id', ondelete='CASCADE'),
        primary_key=True
    )
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey('event_groups.id', ondelete='CASCADE'),
        primary_key=True
    )

    event = relationship(
        "Event",
        foreign_keys=[event_id],
        overlaps="groups,event_group_associations,events"
    )
    group = relationship(
        "EventGroup",
        foreign_keys=[group_id],
        overlaps="events,event_group_associations"
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
    description = Column(Text, nullable=False, default="")
    for_single_user = Column(Boolean, nullable=False)
    link = Column(Text, nullable=False, default="")
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
    comment = Column(Text, nullable=False, default="")

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
