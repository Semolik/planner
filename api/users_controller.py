from fastapi_mail import FastMail, MessageSchema, MessageType
from mail.conf import conf
from fastapi_users.authentication import CookieTransport
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
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.db import SQLAlchemyUserDatabase
from models.user import User, UserRole, UserRoleAssociation
from os import getenv
from db.session import get_async_session, AsyncSession, get_async_session_context
from config import settings
from cruds.base_crud import BaseCRUD


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.SECRET
    verification_token_secret = settings.SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(
            f'Пользователь {user.id} запросил сброс пароля, верифицирован ли он: {user.is_verified}')
        if not user.is_verified:
            return
        message = MessageSchema(
            subject='Сброс пароля',
            # List of recipients, as many as you can pass
            recipients=[user.email],
            template_body={
                'title': 'Сброс пароля',
                'text': f'''<p>Здравствуйте, {user.name}</p>
                            <p>
                                Вы получили это письмо, так
                                как был запрошен сброс
                                пароля для вашей учетной
                                записи. Если вы не
                                запрашивали сброс пароля,
                                пожалуйста, проигнорируйте
                                это сообщение.
                            </p>
                            <p>
                                Никогда не предоставляйте
                                свои учетные данные и не
                                переходите по незнакомым
                                ссылкам.
                            </p>
                            <a
                                href="{getenv('RESET_PASSWORD_URL').format(token=token)}"
                                class="btn btn-primary"
                                target="_blank"
                            >
                                Сбросить пароль
                            </a>'''
            },
            subtype=MessageType.html
        )
        try:
            fm = FastMail(conf)
            await fm.send_message(message, template_name='default.html')
        except Exception as e:
            print(e)

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f'Пользователь {user.id} запросил верификацию')
        message = MessageSchema(
            subject='Подтверждение почты',
            recipients=[user.email],
            template_body={
                'title': 'Подтверждение почты',
                'text': f'''<p>Здравствуйте, {user.name}</p>
                            <p>
                                Для подтверждения вашей учетной записи, пожалуйста, нажмите на кнопку ниже:
                            </p>
                            <a
                                href="{getenv('VERIFY_ACCOUNT_URL').format(token=token)}"
                                class="btn btn-primary"
                                target="_blank"
                            >
                                Подтвердить почту
                            </a>'''
            },
            subtype=MessageType.html
        )
        try:
            fm = FastMail(conf)
            await fm.send_message(message, template_name='default.html')
        except Exception as e:
            print(e)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


cookie_transport = CookieTransport(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(superuser=True)
optional_current_user = fastapi_users.current_user(optional=True)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(email: str, password: str, first_name: str, last_name: str, group: str, institute_id: uuid.UUID, roles: list[UserRole], patronymic: str | None = None, birth_date: str | None = None, vk_username: str | None = None, phone: str | None = None, is_superuser: bool = False, is_verified: bool = True):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    db_user = await user_manager.create(
                        UserCreate(
                            email=email,
                            password=password,
                            is_superuser=is_superuser,
                            is_verified=is_verified,
                            first_name=first_name,
                            last_name=last_name,
                            patronymic=patronymic,
                            group=group,
                            institute_id=institute_id,
                            birth_date=birth_date,
                            vk_username=vk_username,
                            phone=phone,
                        )
                    )
                    for role in roles:
                        await BaseCRUD(session).create(UserRoleAssociation(
                            user_id=db_user.id, role=role))
                    return await user_manager.get(db_user.id)
    except UserAlreadyExists:
        print(f"User {email} already exists")


async def get_user_by_id(id: uuid.UUID):
    async with get_async_session_context() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                return await user_manager.get(id)
