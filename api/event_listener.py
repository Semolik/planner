from utilities.vk import VKUtils
from models.user_models import User

from sqlalchemy import event
from pathlib import Path
from utilities.files import get_file_path, get_image_path
from models.files_models import File, Image
from models.events_models import Event, TaskState


@event.listens_for(Image, "before_delete")
def after_delete_image(mapper, connection, target: Image):
    image_path = get_image_path(image=target)
    path = Path(image_path)
    if path.exists():
        path.unlink()


@event.listens_for(File, "before_delete")
def after_delete_file(mapper, connection, target: File):
    file_path = get_file_path(file=target)
    path = Path(file_path)
    if path.exists():
        path.unlink()


def add_vk_listeners(vk_utils: VKUtils):
    @event.listens_for(User, "after_update")
    def after_update_user(mapper, connection, target: User):
        if target.is_superuser and target.vk_id:
            vk_utils.update_superusers_vk_ids(added_user_id=target.vk_id)

    @event.listens_for(User, "after_delete")
    def after_delete_user(mapper, connection, target: User):
        if target.is_superuser and target.vk_id:
            vk_utils.update_superusers_vk_ids(removed_user_id=target.vk_id)

    @event.listens_for(Event, "after_insert")
    @event.listens_for(Event, "after_delete")
    @event.listens_for(Event, "after_update")
    def receive_event_events(mapper, connection, target: Event):
        vk_utils.update_messages_task()

    @event.listens_for(TaskState, "after_insert")
    @event.listens_for(TaskState, "after_update")
    @event.listens_for(TaskState, "after_delete")
    def receive_task_state_events(mapper, connection, target: TaskState):
        vk_utils.update_messages_task()
