from fastapi_users.authentication import Authenticator
from fastapi_users.authentication.authenticator import name_to_variable_name, name_to_strategy_variable_name, EnabledBackendsDependency
from typing import Optional, Sequence, Tuple
from fastapi import HTTPException, status
from fastapi_users import models
from fastapi_users.authentication.backend import AuthenticationBackend
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.manager import BaseUserManager
from sqlalchemy import select
from makefun import with_signature

from models.user_models import UserRole
from db.session import get_async_session_context

# метод определения подходимости уровня роли


class CustomAuthenticator(Authenticator):
    def current_user(
        self,
        optional: bool = False,
        photographer: bool = False,
        copywriter: bool = False,
        designer: bool = False,
        superuser: bool = False,
        get_enabled_backends: Optional[EnabledBackendsDependency] = None,
    ):

        signature = self._get_dependency_signature(get_enabled_backends)

        @with_signature(signature)
        async def current_user_dependency(*args, **kwargs):
            user, _ = await self._authenticate(
                *args,
                optional=optional,
                photographer=photographer,
                copywriter=copywriter,
                designer=designer,
                superuser=superuser,
                **kwargs,
            )
            return user

        return current_user_dependency

    async def _authenticate(
        self,
        *args,
        user_manager: BaseUserManager[models.UP, models.ID],
        optional: bool = False,
        photographer: bool = False,
        copywriter: bool = False,
        designer: bool = False,
        superuser: bool = False,
        **kwargs,
    ) -> Tuple[Optional[models.UP], Optional[str]]:
        user: Optional[models.UP] = None
        token: Optional[str] = None
        enabled_backends: Sequence[AuthenticationBackend] = kwargs.get(
            "enabled_backends", self.backends
        )

        for backend in self.backends:
            if backend in enabled_backends:
                token = kwargs[name_to_variable_name(backend.name)]
                strategy: Strategy[models.UP, models.ID] = kwargs[
                    name_to_strategy_variable_name(backend.name)
                ]
                if token is not None:
                    user = await strategy.read_token(token, user_manager)
                    if user:
                        break

        if not user and not optional:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходима авторизация"
            )

        if user:
            if not user.is_superuser:
                if photographer and UserRole.PHOTOGRAPHER not in user.roles:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Пользователь не является фотографом",
                    )
                if copywriter and UserRole.COPYWRITER not in user.roles:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Пользователь не является копирайтером",
                    )
                if designer and UserRole.DESIGNER not in user.roles:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Пользователь не является дизайнером",
                    )
            if superuser and not user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Пользователь не является суперпользователем",
                )

        return user, token
