from cruds.settings_crud import SettingsCRUD
from schemas.events import TypedTaskReadFull, UpdateTypedTaskState
import uuid
from fastapi import APIRouter, Depends, HTTPException
from cruds.tasks_crud import TasksCRUD
from cruds.users_crud import UsersCRUD
from users_controller import current_superuser
from db.session import get_async_session
from models.user import User

api_router = APIRouter(prefix="/vk", tags=["vk endpoints"])


@api_router.post('/set-token', status_code=204)
async def set_token(
    token: str,
    db=Depends(get_async_session),
    current_user: User = Depends(current_superuser)
):
    settings_crud = SettingsCRUD(db)
    await settings_crud.set_setting(
        key='vk_token',
        value=token
    )
