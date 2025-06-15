from core.users_controller import get_async_session_context
from sqlalchemy import event
from pathlib import Path
from utilities.files import get_file_path, get_image_path
import asyncio
from models.files_models import File, Image


async def delete_image_file(target: Image):
    async with get_async_session_context() as session:
        image_path = get_image_path(image=target)
        path = Path(image_path)
        if path.exists():
            path.unlink()


async def delete_file(target: File):
    async with get_async_session_context() as session:
        file_path = get_file_path(file=target)
        path = Path(file_path)
        if path.exists():
            print("Deleting file:", path)
            path.unlink()


@event.listens_for(Image, "before_delete")
def receive_after_delete(mapper, connection, target: Image):
    asyncio.create_task(delete_image_file(target=target))


@event.listens_for(File, "before_delete")
def receive_after_delete(mapper, connection, target: File):
    asyncio.create_task(delete_file(target=target))
