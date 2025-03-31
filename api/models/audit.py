from sqlalchemy.orm import object_session
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from db.session import Base
import uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    changed_at = Column(DateTime, server_default=func.now(), nullable=False)
    field_name = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    changed_by = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=True)
    change_type = Column(String, nullable=False)

    user = relationship("User", foreign_keys=[changed_by])


class AuditableMixin:
    def save_audit(self, session: Session, field_name, old_value, new_value, changed_by=None, change_type='UPDATE'):
        audit = AuditLog(
            entity_type=self.__class__.__name__,
            entity_id=self.id,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            changed_by=changed_by.id if changed_by else None,
            change_type=change_type
        )
        # Сохраняем аудит в список вместо прямого добавления
        if not hasattr(session, "_audit_records"):
            session._audit_records = []
        session._audit_records.append(audit)


# Регистрация событий для автоматического логирования
def register_audit_events(base_class):

    @event.listens_for(base_class, 'before_update', propagate=True)
    def before_update_listener(mapper, connection, target):
        session = object_session(target)
        inspector = inspect(target)

        # Проходим по всем измененным полям
        for attr in inspector.attrs:
            hist = inspector.get_history(attr.key, True)
            if hist.has_changes():
                old_value = hist.deleted[0] if hist.deleted else None
                new_value = hist.added[0] if hist.added else None

                target.save_audit(
                    session,
                    field_name=attr.key,
                    old_value=old_value,
                    new_value=new_value,
                    changed_by=getattr(target, 'changed_by', None),
                    change_type='UPDATE'
                )

    @event.listens_for(Session, "after_flush", once=False)
    def after_flush(session, flush_context):
        # Добавляем все записи аудита в сессию после завершения flush
        if hasattr(session, "_audit_records"):
            for audit in session._audit_records:
                session.add(audit)
            # Очищаем список после добавления
            session._audit_records = []
