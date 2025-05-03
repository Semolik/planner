from utilities.files import save_image
from core.users_controller import current_superuser
from schemas.settings import SettingsUpdate, Settings
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from schemas.files import ImageLink
from cruds.settings_crud import SettingsCRUD
from db.session import get_async_session
api_router = APIRouter(prefix="/settings", tags=["settings"])


@api_router.get("", response_model=Settings)
async def get_settings(
    db: Session = Depends(get_async_session)
):
    settings_crud = SettingsCRUD(db)
    return await settings_crud.get_settings()


@api_router.put("/app_logo", response_model=ImageLink, dependencies=[Depends(current_superuser)])
async def set_app_logo(
    image: UploadFile = File(...),
    db: Session = Depends(get_async_session),
):
    settings_crud = SettingsCRUD(db)
    image = await save_image(db=db, upload_file=image)
    await settings_crud.update_app_logo(image=image)
    return image


@api_router.put("", response_model=Settings, dependencies=[Depends(current_superuser)])
async def update_setting(
    settings: SettingsUpdate,
    db: Session = Depends(get_async_session),
):
    settings_crud = SettingsCRUD(db)
    for key, value in settings.model_dump().items():
        await settings_crud.set_setting(key=key, value=str(value))
    return await settings_crud.get_settings()
