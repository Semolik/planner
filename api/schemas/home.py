import uuid
from pydantic import BaseModel
from models.user_models import UserRole

from schemas.files import File


class HomeNoteRead(BaseModel):
    id: uuid.UUID
    text: str
    files: list[File] = []
    role: UserRole
