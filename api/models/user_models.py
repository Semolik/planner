import uuid
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Date, Integer, String, DateTime, func, ForeignKey, Enum
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from models.audit_models import AuditableMixin, register_audit_events
from db.session import Base


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
        "UserRoleAssociation", back_populates="user", cascade="all, delete-orphan"
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


class Requirements(Base):
    __tablename__ = "requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    user_role = Column(Enum(UserRole), nullable=False)
