from users_controller import get_async_session_context
from sqlalchemy import event
from pathlib import Path
from utilities.files import get_image_path
from cruds.base_crud import BaseCRUD
import asyncio
import uuid
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from models.files import Image
from db.session import Base


async def delete_image_file(target: Image):
    async with get_async_session_context() as session:
        image_path = get_image_path(image=target)
        path = Path(image_path)
        if path.exists():
            path.unlink()


@event.listens_for(Image, "before_delete")
def receive_after_delete(mapper, connection, target: Image):
    asyncio.create_task(delete_image_file(target=target))
