from cruds.vk_crud import VKCRUD
from schemas.vk import ChatsSettingsResponse, UpdateChatSettings
from utilities.vk import VKUtils
from cruds.settings_crud import SettingsCRUD
from fastapi import APIRouter, Depends, Form, Request
from core.users_controller import current_superuser
from db.session import get_async_session
from models.user_models import User, UserRole

api_router = APIRouter(prefix="/vk", tags=["vk"])


@api_router.post("/token", status_code=204)
async def set_token(
    request: Request,
    token: str = Form(...),
    db=Depends(get_async_session),
    current_user: User = Depends(current_superuser),
):
    settings_crud = SettingsCRUD(db)
    await settings_crud.set_setting(key="vk_token", value=token)
    vk_utils: VKUtils = request.app.state.vk_utils
    if vk_utils:
        await vk_utils.stop_bot()
        await vk_utils.start_bot(token=token)


@api_router.get(
    "/settings",
    status_code=200,
    response_model=ChatsSettingsResponse,
    dependencies=[Depends(current_superuser)],
)
async def get_status(
    request: Request,
    db=Depends(get_async_session),
):
    vk_utils: VKUtils = request.app.state.vk_utils
    return await VKCRUD(db).get_chats_settings(vk_utils=vk_utils)


@api_router.put(
    "/settings",
    status_code=200,
    dependencies=[Depends(current_superuser)],
    response_model=ChatsSettingsResponse,
)
async def update_settings(
    update_data: UpdateChatSettings, request: Request, db=Depends(get_async_session)
):
    settings_crud = SettingsCRUD(db)
    roles = {
        "photographers": UserRole.PHOTOGRAPHER,
        "copywriters": UserRole.COPYWRITER,
        "designers": UserRole.DESIGNER,
    }
    for role in ["photographers", "copywriters", "designers"]:
        key = f"vk_chat_{role}_enabled"
        await settings_crud.set_setting(
            key=key,
            value="true"
            if getattr(update_data, f"vk_chat_{role}_enabled")
            else "false",
        )
        if not getattr(update_data, f"vk_chat_{role}_enabled"):
            chat = await VKCRUD(db).get_chat_by_role(roles[role])
            if chat:
                await VKCRUD(db).delete(chat)
    vk_utils: VKUtils = request.app.state.vk_utils
    return await VKCRUD(db).get_chats_settings(vk_utils=vk_utils)


@api_router.delete("/token", status_code=204, dependencies=[Depends(current_superuser)])
async def delete_token(request: Request, db=Depends(get_async_session)):
    settings_crud = SettingsCRUD(db)
    setting = await settings_crud.get_setting("vk_token")
    if setting:
        await settings_crud.delete(setting)
    vk_utils: VKUtils = request.app.state.vk_utils
    print("Stopping VK bot...")
    if vk_utils:
        print("VK bot found, stopping...")
        await vk_utils.stop_bot()
