import uuid
from sqlalchemy import select
from models.app_models import AppSettings
from schemas.settings import Settings
from cruds.base_crud import BaseCRUD
from cruds.file_cruds import FilesCRUD
from models.files_models import Image


class SettingsCRUD(BaseCRUD):
    async def get_setting(self, key: str) -> AppSettings:
        query = select(AppSettings).where(AppSettings.key == key)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def set_setting(self, key: str, value: str) -> AppSettings:
        setting = await self.get_setting(key)
        if setting:
            setting.value = value
            return await self.update(setting)
        else:
            setting = AppSettings(key=key, value=value)
            return await self.create(setting)

    async def update_app_logo(self, image: Image) -> AppSettings:
        setting = await self.get_setting("app_logo")
        if setting:
            await self.db.delete(
                await FilesCRUD(self.db).get_image_by_id(uuid.UUID(setting.value))
            )
            setting.value = str(image.id)
            await self.update(setting)
        else:
            setting = AppSettings(key=str("app_logo"), value=str(image.id))
            await self.create(setting)
        return setting

    async def get_image(self) -> Image | None:
        setting = await self.get_setting("app_logo")
        if setting:
            return await FilesCRUD(self.db).get_image_by_id(uuid.UUID(setting.value))
        return None

    async def get_settings(self) -> Settings:
        query = select(AppSettings)
        result = await self.db.execute(query)
        settings = result.scalars().all()
        app_logo = await self.get_image()
        app_name = list(filter(lambda x: x.key == "app_name", settings))
        designers_deadline = list(
            filter(lambda x: x.key == "designers_deadline", settings)
        )
        photographers_deadline = list(
            filter(lambda x: x.key == "photographers_deadline", settings)
        )
        copywriters_deadline = list(
            filter(lambda x: x.key == "copywriters_deadline", settings)
        )
        default_event_level_id = list(
            filter(lambda x: x.key == "default_event_level_id", settings)
        )
        return Settings(
            app_logo=app_logo,
            app_name=app_name[0].value,
            designers_deadline=int(designers_deadline[0].value),
            photographers_deadline=int(photographers_deadline[0].value),
            copywriters_deadline=int(copywriters_deadline[0].value),
            default_event_level_id=uuid.UUID(default_event_level_id[0].value)
            if default_event_level_id
            else None,
        )
