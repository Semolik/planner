import uuid
from sqlalchemy import select
from api.models.home_models import HomeFile, HomeNote
from api.models.user_models import UserRole
from api.cruds.base_crud import BaseCRUD
from sqlalchemy.orm import selectinload


class HomeCRUD(BaseCRUD):
    async def get_home_notes(self, roles: list[UserRole]):
        query = (
            select(HomeNote)
            .where(HomeNote.role.in_(roles))
            .options(selectinload(HomeNote.files))
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_home_note(self, text: str, role: UserRole):
        return await self.create(HomeNote(text=text, role=role))

    async def get_note_by_type(self, role: UserRole):
        query = select(HomeNote).where(HomeNote.role == role)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_note_by_id(self, note_id: uuid.UUID):
        query = (
            select(HomeNote)
            .where(HomeNote.id == note_id)
            .options(selectinload(HomeNote.files))
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_note_file_relationship(self, note_id: uuid.UUID, file_id: uuid.UUID):
        query = select(HomeFile).where(
            HomeFile.home_note_id == note_id, HomeFile.file_id == file_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update_note(self, note: HomeNote, text: str):
        note.text = text
        return await self.update(note)

    async def add_file_to_note(self, note_id: uuid.UUID, file_id: uuid.UUID):
        await self.create(HomeFile(home_note_id=note_id, file_id=file_id))
