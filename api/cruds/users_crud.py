import uuid
from sqlalchemy import select, or_, nulls_first
from sqlalchemy.orm import selectinload

from cruds.base_crud import BaseCRUD
from models.user import User
from schemas.users import UserUpdate
from users_controller import get_user_manager_context


class UsersCRUD(BaseCRUD):
    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        query = await self.db.execute(select(User).where(User.id == user_id).options(
            selectinload(User.institute), selectinload(User.roles_objects)))
        return query.scalars().first()

    async def get_user_by_email(self, email: str) -> User:
        user = select(User).where(User.email == email)
        result = await self.db.execute(user)
        return result.scalars().first()

    async def get_users(self, order_by: str = "last_name", order: str = "asc", search: str = None, page: int = 1, superusers_to_top: bool = False, only_superusers: bool = False,
                        page_size: int = 20) -> list[User]:
        order_query = getattr(User, order_by).asc(
        ) if order == "asc" else getattr(User, order_by).desc()
        users = select(User)
        if superusers_to_top:
            users = users.order_by(nulls_first(
                User.is_superuser.desc()), order_query)
        else:
            users = users.order_by(order_query)
        if search:
            users = users.where(
                or_(User.first_name.ilike(f"%{search}%"), User.last_name.ilike(
                    f"%{search}%")), User.patronymic.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"),
                User.vk_username.ilike(f"%{search}%"), User.phone.ilike(f"%{search}%"), User.group.ilike(f"%{search}%"))
        if only_superusers:
            users = users.where(User.is_superuser == True)
        users = users.offset(
            (page - 1) * page_size).limit(page_size)
        result = await self.db.execute(users.options(selectinload(User.institute), selectinload(User.roles_objects)))
        return result.scalars().all()

    async def update_user(self, user: User, user_data: UserUpdate, update_as_superuser: bool = False) -> User:
        if update_as_superuser:
            user.is_superuser = user_data.is_superuser
            user.is_active = user_data.is_active
            user.is_verified = user_data.is_verified
            user.group = user_data.group
            user.institute_id = user_data.institute_id
            user.roles = user_data.roles
        user.first_name = user_data.first_name
        user.last_name = user_data.last_name
        user.patronymic = user_data.patronymic
        user.vk_username = user_data.vk_username
        user.birth_date = user_data.birth_date
        user.phone = user_data.phone

        if user_data.password:
            async with get_user_manager_context(self.db) as user_manager:
                user.hashed_password = user_manager.password_helper.hash(
                    user_data.password)
        if user.email != user_data.email:
            user.email = user_data.email
            user.is_verified = False if not update_as_superuser else user_data.is_verified
            user = await self.update(user)
            async with get_user_manager_context(self.db) as user_manager:
                await user_manager.request_verify(user)
        else:
            user = await self.update(user)
        return user

    async def has_admin(self) -> bool:
        query = await self.db.execute(select(User).where(User.is_superuser == True))
        return query.scalar() is not None
