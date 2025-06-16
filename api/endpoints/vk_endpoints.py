from utilities.vk import VKUtils
from cruds.settings_crud import SettingsCRUD
from schemas.events import TypedTaskReadFull, UpdateTypedTaskState
import uuid
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from cruds.tasks_crud import TasksCRUD
from cruds.users_crud import UsersCRUD
from core.users_controller import current_superuser
from db.session import get_async_session
from models.user_models import User

api_router = APIRouter(prefix="/vk", tags=["vk"])


@api_router.post('/token', status_code=204)
async def set_token(
    request: Request,
    token: str = Form(...),
    db=Depends(get_async_session),
    current_user: User = Depends(current_superuser)
):
    settings_crud = SettingsCRUD(db)
    await settings_crud.set_setting(
        key='vk_token',
        value=token
    )
    vk_utils: VKUtils = request.app.state.vk_utils
    if vk_utils:
        await vk_utils.stop_bot()
        await vk_utils.start_bot(token=token)


@api_router.get('/token/status', status_code=200, response_model=bool, dependencies=[Depends(current_superuser)])
async def get_token_status(
    db=Depends(get_async_session)
):
    settings_crud = SettingsCRUD(db)
    setting = await settings_crud.get_setting('vk_token')
    return bool(setting and setting.value.strip() != '')


@api_router.delete('/token', status_code=204, dependencies=[Depends(current_superuser)])
async def delete_token(
    request: Request,
    db=Depends(get_async_session)

):
    settings_crud = SettingsCRUD(db)
    setting = await settings_crud.get_setting('vk_token')
    if setting:
        await settings_crud.delete(setting)
    vk_utils: VKUtils = request.app.state.vk_utils
    print("Stopping VK bot...")
    if vk_utils:
        print("VK bot found, stopping...")
        await vk_utils.stop_bot()
