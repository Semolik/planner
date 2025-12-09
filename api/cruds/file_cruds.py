import uuid

from api.cruds.base_crud import BaseCRUD
from api.models.files_models import File, Image


class FilesCRUD(BaseCRUD):
    async def get_image_by_id(self, image_id: uuid.UUID) -> Image:
        return await self.get(image_id, Image)

    async def get_file_by_id(self, file_id: uuid.UUID) -> File:
        return await self.get(file_id, File)
