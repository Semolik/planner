import uuid
import enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Date, Integer, String, DateTime, func, ForeignKey, Enum
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from api.models.audit_models import AuditableMixin, register_audit_events
from api.db.session import Base


class UserRole(enum.Enum):
    PHOTOGRAPHER = "photographer"
    COPYWRITER = "copywriter"
    DESIGNER = "designer"


class User(SQLAlchemyBaseUserTableUUID, Base, AuditableMixin):
    __tablename__ = "users"
    email = None

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    patronymic = Column(String, nullable=False, default="")
    vk_id = Column(Integer, nullable=True)

    birth_date = Column(Date, nullable=True)
    phone = Column(String, nullable=False, default="")
    group = Column(String, nullable=False)
    institute_id = Column(
        UUID(as_uuid=True), ForeignKey("institutes.id"), nullable=False
    )

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    roles_objects = relationship(
        "UserRoleAssociation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def roles(self):
        return [role.role for role in self.roles_objects]

    institute = relationship("Institute", foreign_keys=[institute_id])


register_audit_events(User)


class UserRoleAssociation(Base):
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(UserRole), primary_key=True)

    user = relationship("User", back_populates="roles_objects", foreign_keys=[user_id])


class Institute(Base):
    __tablename__ = "institutes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)


class RequiredPeriod(Base):
    __tablename__ = "required_periods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_start: Mapped[Date] = mapped_column(Date, nullable=False)
    period_end: Mapped[Date] = mapped_column(Date, nullable=False)
    roles_config = relationship(
        "RolePeriodConfig",
        back_populates="required_period",
        cascade="all, delete-orphan",
    )


class RolePeriodConfig(Base):
    __tablename__ = "required_period_configs"

    required_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("required_periods.id", ondelete="CASCADE"),
        primary_key=True,
    )
    required_period: Mapped["RequiredPeriod"] = relationship(
        "RequiredPeriod",
        back_populates="roles_config",
        foreign_keys=[required_period_id],
    )
    user_role: Mapped[UserRole] = mapped_column(Enum(UserRole), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class CustomAchievementModel(Base):
    __tablename__ = "custom_achievements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date_from: Mapped[Date] = mapped_column(Date, nullable=False)
    date_to: Mapped[Date | None] = mapped_column(Date, nullable=True)
    level_of_participation: Mapped[str | None] = mapped_column(String, nullable=True)
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    link: Mapped[str | None] = mapped_column(String, nullable=True)
    achievement_level: Mapped[str | None] = mapped_column(String, nullable=True)
