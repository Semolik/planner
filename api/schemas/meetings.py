import uuid

from pydantic import BaseModel
from datetime import date


class MeetingCreate(BaseModel):
    date: date


class MeetingUpdate(MeetingCreate):
    pass


class MeetingRead(MeetingUpdate):
    id: uuid.UUID

    class Config:
        from_attributes = True
