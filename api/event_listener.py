from core.users_controller import get_async_session_context
from sqlalchemy import event
from pathlib import Path
from utilities.files import get_image_path
import asyncio
from models.files import Image


async def delete_image_file(target: Image):
    async with get_async_session_context() as session:
        image_path = get_image_path(image=target)
        path = Path(image_path)
        if path.exists():
            path.unlink()


@event.listens_for(Image, "before_delete")
def receive_after_delete(mapper, connection, target: Image):
    asyncio.create_task(delete_image_file(target=target))
