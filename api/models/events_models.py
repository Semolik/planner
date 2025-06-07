import uuid
from pytest import Session
from sqlalchemy.orm import relationship, column_property, object_session
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Enum, Integer, String, ForeignKey, Text, Boolean, UniqueConstraint, TIMESTAMP, Date, Time, select
from sqlalchemy.sql import func
from models.user_models import UserRole
from models.audit_models import AuditLog, AuditableMixin, register_audit_events
from db.session import Base


class EventLevel(Base):
    __tablename__ = "event_levels"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, unique=True)
    order = Column(Integer, nullable=False, default=0)


class Event(Base, AuditableMixin):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    name_approved = Column(Boolean, nullable=False, default=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(String, nullable=False)
    organizer = Column(String, nullable=False, default="")
    link = Column(Text, nullable=False, default="")
    required_photographers = Column(
        Integer, nullable=False)
    description = Column(Text, nullable=False, default="")
    level_id = Column(
        UUID(as_uuid=True),
        ForeignKey('event_levels.id', ondelete='SET NULL'),
        nullable=True
    )
    level = column_property(
        select(EventLevel.name).where(EventLevel.id ==
                                      level_id).correlate_except(EventLevel).scalar_subquery()
    )
    field_labels = {
        "name": "Название",
        "name_approved": "Название утверждено",
        "date": "Дата проведения",
        "location": "Место проведения",
        "organizer": "Организатор",
        "link": "Ссылка на мероприятие",
        "required_photographers": "Количество фотографов",
        "description": "Описание",
        "start_time": "Время начала",
        "end_time": "Время окончания",
    }
    # Внешний ключ на EventGroup (событие принадлежит одной группе)
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey('event_groups.id', ondelete='CASCADE'),
        nullable=True
    )

    # Связь с EventGroup
    group = relationship(
        "EventGroup",
        foreign_keys=[group_id],
        back_populates="events",
        cascade="all, delete-orphan",
        single_parent=True
    )

    # Cascade deletion for Task
    task = relationship(
        "Task",
        uselist=False,
        back_populates="event",
        cascade="all, delete-orphan",
        single_parent=True
    )


class PersonalEvent(Base):
    __tablename__ = "personal_events"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    role = Column(String, nullable=False, default="")
    level = Column(String, nullable=False, default="")
    approve_link = Column(Text, nullable=False, default="")


class EventGroup(Base, AuditableMixin):
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


class TasksToken(Base):
    __tablename__ = "tasks_token"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    token = Column(String, nullable=False, default="")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        server_default=func.now(), onupdate=func.now())
    role = Column(Enum(UserRole), nullable=False)


class TypedTask(Base, AuditableMixin):
    __tablename__ = "typed_tasks"
    __table_args__ = (
        UniqueConstraint(
            'task_id', 'task_type',
            name='uq_typed_task_task_id_task_type'
        ),
    )
    due_date = Column(TIMESTAMP(timezone=True), nullable=True)
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False
    )
    task_type = Column(Enum(UserRole), nullable=False)
    description = Column(Text, nullable=False, default="")
    for_single_user = Column(Boolean, nullable=False)
    link = Column(Text, nullable=False, default="")
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

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)

    __table_args__ = (
        UniqueConstraint(
            'type_task_id', 'user_id',
            name='uq_task_states_type_task_id_user_id'
        ),
    )

    type_task_id = Column(
        UUID(as_uuid=True),
        ForeignKey('typed_tasks.id', ondelete='CASCADE'),
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    is_completed = Column(Boolean, nullable=False, default=False)
    comment = Column(Text, nullable=False, default="")

    typed_task = relationship(
        "TypedTask",
        foreign_keys=[type_task_id],
        uselist=False,
        overlaps="users",
        back_populates="task_states"
    )
    user = relationship(
        "User",
        foreign_keys=[user_id],
        uselist=False,
        overlaps="users"
    )
    period = relationship(
        "TaskStatePeriod",
        back_populates="task_state",
        cascade="all, delete-orphan",
        single_parent=True
    )


class TaskStatePeriod(Base):
    __tablename__ = 'task_states_periods'
    __table_args__ = (
        UniqueConstraint(
            'task_state_id', 'period_start', 'period_end',
            name='uq_task_state_periods_task_state_id_period_start_period_end'
        ),
    )
    task_state_id = Column(
        UUID(as_uuid=True),
        ForeignKey('task_states.id', ondelete='CASCADE'),
        primary_key=True
    )
    period_start = Column(Time, nullable=False)
    period_end = Column(Time, nullable=False)
    task_state = relationship(
        "TaskState",
        foreign_keys=[task_state_id],
        uselist=False,
        back_populates="period",
        cascade="all, delete-orphan",
        single_parent=True
    )


register_audit_events(Event, tracked_fields=[
    "name",
    "name_approved",
    "date",
    "location",
    "organizer",
    "link",
    "required_photographers",
    "description",
    "start_time",
    "end_time"
])
register_audit_events(EventGroup, tracked_fields=[
    "name",
    "description",
    "organizer",
    "link"
])
register_audit_events(TypedTask, tracked_fields=[
    "task_id",
    "task_type",
    "description",
    "for_single_user",
    "link"
])
