import enum
import uuid
from datetime import datetime, date, time

from sqlalchemy.orm import relationship, mapped_column, Mapped, column_property
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Enum,
    Integer,
    String,
    ForeignKey,
    Text,
    Boolean,
    UniqueConstraint,
    TIMESTAMP,
    Date,
    Time,
    select,
    case,
)
from sqlalchemy.sql import func
from models.files_models import File, Image
from models.user_models import UserRole
from models.audit_models import AuditableMixin, register_audit_events
from db.session import Base


class EventLevel(Base):
    __tablename__ = "event_levels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Event(Base, AuditableMixin):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    name_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    organizer: Mapped[str] = mapped_column(String, nullable=False, default="")
    link: Mapped[str] = mapped_column(Text, nullable=False, default="")
    required_photographers: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    level_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("event_levels.id", ondelete="SET NULL"),
        nullable=True,
    )
    level = column_property(
        select(EventLevel.name)
        .where(EventLevel.id == level_id)
        .correlate_except(EventLevel)
        .scalar_subquery()
    )

    is_passed = column_property(
        case(
            (date < func.current_date(), True),
            (date == func.current_date(), end_time < func.current_time()),
            else_=False,
        )
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
    group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("event_groups.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Связь с EventGroup
    group = relationship("EventGroup", foreign_keys=[group_id], single_parent=True)

    # Cascade deletion for Task
    task = relationship(
        "Task",
        uselist=False,
        back_populates="event",
        cascade="all, delete-orphan",
        single_parent=True,
    )


class PersonalEvent(Base):
    __tablename__ = "personal_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="")
    level: Mapped[str] = mapped_column(String, nullable=False, default="")
    approve_link: Mapped[str] = mapped_column(Text, nullable=False, default="")


class EventGroup(Base, AuditableMixin):
    __tablename__ = "event_groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    organizer: Mapped[str] = mapped_column(String, nullable=False, default="")
    link: Mapped[str] = mapped_column(Text, nullable=False, default="")
    events = relationship(
        "Event",
        back_populates="group",
        foreign_keys=[Event.group_id],
        single_parent=True,
    )
    period_start = column_property(
        select(func.min(Event.date))
        .where(Event.group_id == id)
        .correlate_except(Event)
        .scalar_subquery()
    )
    period_end = column_property(
        select(func.max(Event.date))
        .where(Event.group_id == id)
        .correlate_except(Event)
        .scalar_subquery()
    )
    events_count = column_property(
        select(func.count(Event.id))
        .where(Event.group_id == id)
        .correlate_except(Event)
        .scalar_subquery()
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=True
    )
    due_date: Mapped[date | None] = mapped_column(Date)

    event = relationship(
        "Event",
        foreign_keys=[event_id],
        uselist=False,
        back_populates="task",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    typed_tasks = relationship(
        "TypedTask",
        back_populates="parent_task",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    files = relationship(
        File, secondary="task_files", overlaps="task_files", viewonly=True
    )
    images = relationship(
        Image, secondary="task_images", overlaps="task_images", viewonly=True
    )


class TaskFile(Base):
    __tablename__ = "task_files"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(Task.id, ondelete="CASCADE"), primary_key=True
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
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


class TaskImage(Base):
    __tablename__ = "task_images"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(Task.id, ondelete="CASCADE"), primary_key=True
    )
    image_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(Image.id, ondelete="CASCADE"), primary_key=True
    )
    image = relationship(
        Image,
        foreign_keys=[image_id],
        uselist=False,
        overlaps="task_images",
        cascade="all, delete-orphan",
        single_parent=True,
    )


class TasksToken(Base):
    __tablename__ = "tasks_token"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    token: Mapped[str] = mapped_column(String, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)


class TypedTask(Base, AuditableMixin):
    __tablename__ = "typed_tasks"
    __table_args__ = (
        UniqueConstraint(
            "task_id", "task_type", name="uq_typed_task_task_id_task_type"
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    task_type: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    for_single_user: Mapped[bool] = mapped_column(Boolean, nullable=False)
    link: Mapped[str] = mapped_column(Text, nullable=False, default="")
    due_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    due_date_passed = column_property(
        case((due_date < func.now(), True), else_=False)
    )
    parent_task = relationship(
        "Task",
        foreign_keys=[task_id],
        uselist=False,
        back_populates="typed_tasks",
        single_parent=True,
    )

    task_states = relationship(
        "TaskState", back_populates="typed_task", cascade="all, delete-orphan"
    )

    users = relationship(
        "User",
        secondary="task_states",
        primaryjoin="and_(TypedTask.id == TaskState.type_task_id)",
        secondaryjoin="and_(User.id == TaskState.user_id)",
        overlaps="task_states",
        viewonly=True,
    )

    field_labels = {
        "task_id": "Задача",
        "task_type": "Тип задачи",
        "description": "Описание",
        "for_single_user": "Для одного пользователя",
        "link": "Ссылка на задачу",
        "due_date": "Срок выполнения",
    }


class State(enum.Enum):
    PENDING = "pending"
    CANCELED = "canceled"
    COMPLETED = "completed"


class TaskState(Base):
    __tablename__ = "task_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    __table_args__ = (
        UniqueConstraint(
            "type_task_id", "user_id", name="uq_task_states_type_task_id_user_id"
        ),
    )

    type_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("typed_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    state: Mapped[State] = mapped_column(
        Enum(State), nullable=False, default=State.PENDING
    )
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="")

    typed_task = relationship(
        "TypedTask",
        foreign_keys=[type_task_id],
        uselist=False,
        overlaps="users",
        back_populates="task_states",
    )
    user = relationship("User", foreign_keys=[user_id], uselist=False, overlaps="users")
    period = relationship(
        "TaskStatePeriod",
        back_populates="task_state",
        cascade="all, delete-orphan",
        single_parent=True,
        uselist=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TaskStatePeriod(Base):
    __tablename__ = "task_states_periods"
    __table_args__ = (
        UniqueConstraint(
            "task_state_id",
            "period_start",
            "period_end",
            name="uq_task_state_periods_task_state_id_period_start_period_end",
        ),
    )
    task_state_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_states.id", ondelete="CASCADE"),
        primary_key=True,
    )
    period_start: Mapped[time] = mapped_column(Time, nullable=False)
    period_end: Mapped[time] = mapped_column(Time, nullable=False)
    task_state = relationship(
        "TaskState",
        foreign_keys=[task_state_id],
        uselist=False,
        back_populates="period",
    )
Event.has_assigned_photographers = column_property(
            select(func.count(TaskState.user_id))
            .select_from(TaskState)
            .join(TypedTask, TypedTask.id == TaskState.type_task_id)
            .join(Task, Task.id == TypedTask.task_id)
            .where(
                Task.event_id == Event.id,
                TypedTask.task_type == UserRole.PHOTOGRAPHER,
                TaskState.state != State.CANCELED,
            )
            .correlate_except(Task, TypedTask, TaskState)
            .scalar_subquery() > 0
        )

register_audit_events(
    Event,
    tracked_fields=[
        "name",
        "name_approved",
        "date",
        "location",
        "organizer",
        "link",
        "required_photographers",
        "description",
        "start_time",
        "end_time",
    ],
)
register_audit_events(
    EventGroup, tracked_fields=["name", "description", "organizer", "link"]
)
register_audit_events(
    TypedTask,
    tracked_fields=["task_id", "task_type", "description", "for_single_user", "link"],
)
