import uuid
from asyncio import Task
from datetime import date

from sqlalchemy import delete, insert, select, or_, nulls_first, func
from sqlalchemy.orm import selectinload

from api.cruds.base_crud import BaseCRUD
from api.models.user_models import User, UserRole, UserRoleAssociation
from api.schemas.users import UserUpdate
from api.core.users_controller import get_user_manager_context


class UsersCRUD(BaseCRUD):
    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        query = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.institute), selectinload(User.roles_objects))
        )
        return query.scalars().first()

    async def get_user_by_vk_id(self, vk_id: int) -> User:
        query = select(User).where(User.vk_id == vk_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_user_by_username(self, username: str) -> User:
        user = select(User).where(User.username == username)
        result = await self.db.execute(user)
        return result.scalars().first()

    async def get_users_by_birthday_period(
        self, date_from: date, date_to: date
    ) -> list[User]:
        month = func.extract("month", User.birth_date)
        day = func.extract("day", User.birth_date)

        from_month = date_from.month
        to_month = date_to.month
        from_day = date_from.day
        to_day = date_to.day

        # Если период не переходит через конец года
        if (from_month, from_day) <= (to_month, to_day):
            condition = (
                (month > from_month) | ((month == from_month) & (day >= from_day))
            ) & ((month < to_month) | ((month == to_month) & (day <= to_day)))
        else:
            # Период переходит через конец года (например, с декабря по январь)
            condition = (
                (month > from_month)
                | ((month == from_month) & (day >= from_day))
                | (month < to_month)
                | ((month == to_month) & (day <= to_day))
            )

        users = select(User).where(condition)
        result = await self.db.execute(
            users.options(
                selectinload(User.institute), selectinload(User.roles_objects)
            )
        )
        return result.scalars().all()

    async def get_users(
        self,
        order_by: str = "last_name",
        order: str = "asc",
        search: str = None,
        page: int = 1,
        superusers_to_top: bool = False,
        only_superusers: bool = False,
        filter_role: UserRole = None,
        page_size: int = 20,
    ) -> list[User]:
        order_query = (
            getattr(User, order_by).asc()
            if order == "asc"
            else getattr(User, order_by).desc()
        )
        users = select(User)
        if superusers_to_top:
            users = users.order_by(nulls_first(User.is_superuser.desc()), order_query)
        else:
            users = users.order_by(order_query)
        if filter_role:
            users = users.join(
                UserRoleAssociation, UserRoleAssociation.user_id == User.id
            ).where(UserRoleAssociation.role == filter_role)
        if search and search.strip():
            search = search.strip()
            users = users.where(
                or_(
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                    User.patronymic.ilike(f"%{search}%"),
                    User.phone.ilike(f"%{search}%"),
                    User.group.ilike(f"%{search}%"),
                )
            )
        if only_superusers:
            users = users.where(User.is_superuser)
        users = users.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(
            users.options(
                selectinload(User.institute),
                selectinload(User.roles_objects),
            )
        )
        return result.scalars().all()

    async def update_user(
        self, user: User, user_data: UserUpdate, update_as_superuser: bool = False
    ) -> User:
        if update_as_superuser:
            user.is_superuser = user_data.is_superuser
            user.is_active = user_data.is_active
            user.is_verified = user_data.is_verified
            user.group = user_data.group
            user.institute_id = user_data.institute_id

            current_roles_query = await self.db.execute(
                select(UserRoleAssociation.role).where(
                    UserRoleAssociation.user_id == user.id
                )
            )
            current_roles = set(current_roles_query.scalars().all())
            new_roles = set(user_data.roles)

            for role in current_roles - new_roles:
                await self.db.execute(
                    delete(UserRoleAssociation).where(
                        UserRoleAssociation.user_id == user.id,
                        UserRoleAssociation.role == role,
                    )
                )
                await self.db.commit()
            for role in new_roles - current_roles:
                await self.db.execute(
                    insert(UserRoleAssociation).values(user_id=user.id, role=role)
                )
                await self.db.commit()

            # Commit changes to DB once after all operations
            await self.db.commit()
        user.first_name = user_data.first_name
        user.last_name = user_data.last_name
        user.patronymic = user_data.patronymic
        user.vk_id = user_data.vk_id
        user.birth_date = user_data.birth_date
        user.phone = user_data.phone

        if user_data.password:
            async with get_user_manager_context(self.db) as user_manager:
                user.hashed_password = user_manager.password_helper.hash(
                    user_data.password
                )
        if user.username != user_data.username:
            user.username = user_data.username
            user.is_verified = (
                False if not update_as_superuser else user_data.is_verified
            )
        return await self.update(user)

    async def has_admin(self) -> bool:
        query = await self.db.execute(select(User).where(User.is_superuser))
        return query.scalar() is not None
