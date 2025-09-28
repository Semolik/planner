import uuid

from sqlalchemy import func, select

from cruds.base_crud import BaseCRUD
from models.user_models import Institute, User


class InstitutesCRUD(BaseCRUD):
    async def get_institute_by_id(self, institute_id: uuid.UUID) -> Institute:
        return await self.get(institute_id, Institute)

    async def get_institutes(self) -> list[Institute]:
        query = select(Institute)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_institute(self, name: str) -> Institute:
        institute = Institute(name=name)
        return await self.create(institute)

    async def update_institute(self, institute: Institute, name: str) -> Institute:
        institute.name = name
        return await self.update(institute)

    async def has_connected_users(self, institute: Institute) -> bool:
        query = select(User).where(User.institute_id == institute.id)
        result = await self.db.execute(query)
        return bool(result.scalars().first())

    async def get_institute_by_name(self, name: str) -> Institute | None:
        query = select(Institute).where(func.lower(Institute.name) == name.lower())
        result = await self.db.execute(query)
        return result.scalars().first()
