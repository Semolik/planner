from fastapi import FastAPI
from utilities.vk import VKUtils
from models.user_models import User
from core.users_controller import get_async_session_context
from sqlalchemy import event
from pathlib import Path
from utilities.files import get_file_path, get_image_path
import asyncio
from models.files_models import File, Image
from models.events_models import Event, TaskState


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


def add_vk_listeners(vk_utils: VKUtils):
    @event.listens_for(User, "after_update")
    def receive_after_update(mapper, connection, target: User):
        if target.is_superuser and target.vk_id:
            vk_utils.update_superusers_vk_ids(
                added_user_id=target.vk_id)

    @event.listens_for(User, "after_delete")
    def receive_after_delete(mapper, connection, target: User):
        if target.is_superuser and target.vk_id:
            vk_utils.update_superusers_vk_ids(
                removed_user_id=target.vk_id)

    @event.listens_for(Event, "after_insert")
    @event.listens_for(Event, "after_delete")
    @event.listens_for(Event, "after_update")
    def receive_after_update(mapper, connection, target: Event):
        vk_utils.update_messages_task()

    @event.listens_for(TaskState, "after_insert")
    @event.listens_for(TaskState, "after_update")
    @event.listens_for(TaskState, "after_delete")
    def receive_after_update(mapper, connection, target: TaskState):
        vk_utils.update_messages_task()
