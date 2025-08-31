
from fastapi_users.authentication import CookieTransport
from sqlalchemy import select
from cruds.base_crud import BaseCRUD
from core.authenticator import CustomAuthenticator
from schemas.users import UserCreate
import uuid
from typing import Optional
import contextlib
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    JWTStrategy,
)
from fastapi_users.exceptions import UserAlreadyExists, UserNotExists
from fastapi_users.db import SQLAlchemyUserDatabase
from models.user_models import User, UserRole, UserRoleAssociation

from db.session import get_async_session, AsyncSession, get_async_session_context
from core.config import settings


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.SECRET
    verification_token_secret = settings.SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.email} has registered.")

    async def get_by_email(self, user_email: str):
        async with get_async_session_context() as session:
            query = await session.execute(
                select(User).where(User.username == user_email))
            user = query.scalars().first()
            if user is None:
                raise UserNotExists()
            return user

    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Optional[Request] = None,
    ):

        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.username)
        if existing_user is not None:
            raise UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


cookie_transport = CookieTransport(
    cookie_max_age=3600, cookie_domain=settings.COOKIE_DOMAIN)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


class CustomFastAPIUsers(FastAPIUsers[User, uuid.UUID]):
    def __init__(
        self,
    ):
        self.authenticator = CustomAuthenticator(
            [auth_backend], get_user_manager)
        self.get_user_manager = get_user_manager
        self.current_user = self.authenticator.current_user


fastapi_users = CustomFastAPIUsers()

current_photographer = fastapi_users.current_user(photographer=True)
current_copywriter = fastapi_users.current_user(copywriter=True)
current_designer = fastapi_users.current_user(designer=True)
current_superuser = fastapi_users.current_user(superuser=True)
optional_current_user = fastapi_users.current_user(optional=True)
current_user = fastapi_users.current_user()
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(username: str, password: str, first_name: str, last_name: str, group: str, institute_id: uuid.UUID, roles: list[UserRole], patronymic: str | None = None, birth_date: str | None = None, vk_id: int | None = None, phone: str | None = None, is_superuser: bool = False, is_verified: bool = True):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    db_user = await user_manager.create(
                        UserCreate(
                            username=username,
                            password=password,
                            is_superuser=is_superuser,
                            is_verified=is_verified,
                            first_name=first_name,
                            last_name=last_name,
                            patronymic=patronymic,
                            group=group,
                            institute_id=institute_id,
                            birth_date=birth_date,
                            vk_id=vk_id,
                            phone=phone,
                        )
                    )
                    for role in roles:
                        await BaseCRUD(session).create(UserRoleAssociation(
                            user_id=db_user.id, role=role))
                    return await user_manager.get(db_user.id)
    except UserAlreadyExists:
        print(f"User {username} already exists")


async def get_user_by_id(id: uuid.UUID):
    async with get_async_session_context() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                return await user_manager.get(id)
