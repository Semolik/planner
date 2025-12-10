from api.cruds.institutes_crud import InstitutesCRUD
from api.cruds.periods_crud import PeriodsCRUD
from api.cruds.tasks_crud import TasksCRUD
from api.models.user_models import User, UserRole
from typing import List, Literal, Union
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import TypeAdapter
from api.cruds.users_crud import UsersCRUD
from api.schemas.events import TypedTaskReadFull
from api.schemas.users import UserRead, UserReadWithEmail, UserUpdate
from api.core.users_controller import (
    current_user,
    current_superuser,
    optional_current_user,
)
from api.db.session import get_async_session


api_router = APIRouter(prefix="/users", tags=["users"])


async def update_handler(db, user: User, user_data: UserUpdate, current_user: User):
    users_crud = UsersCRUD(db)
    if not current_user.is_superuser and current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    if current_user.is_superuser:
        if user.id == current_user.id and not user_data.is_superuser:
            raise HTTPException(
                status_code=403, detail="Нельзя понизить себя до обычного пользователя"
            )
    if (
        user_data.username != user.username
        and await users_crud.get_user_by_username(user_data.username) is not None
    ):
        raise HTTPException(
            status_code=400, detail="Пользователь с таким username уже существует"
        )
    if user_data.institute_id != user.institute_id:
        institute_crud = InstitutesCRUD(db)
        if not await institute_crud.get_institute_by_id(user_data.institute_id):
            raise HTTPException(status_code=400, detail="Институт не найден")
    await users_crud.update_user(
        user=user, user_data=user_data, update_as_superuser=current_user.is_superuser
    )
    return await users_crud.get_user_by_id(user.id)


@api_router.put("/{user_id}", response_model=UserReadWithEmail)
async def update_user(
    user: UserUpdate,
    user_id: uuid.UUID,
    db=Depends(get_async_session),
    current_user: User = Depends(current_superuser),
):
    users_crud = UsersCRUD(db)
    db_user = await users_crud.get_user_by_id(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return await update_handler(
        db=db, user=db_user, user_data=user, current_user=current_user
    )


@api_router.get("/me", response_model=UserReadWithEmail, name="users:current_user")
async def get_user_me(
    db=Depends(get_async_session), current_user: User = Depends(current_user)
):
    return await UsersCRUD(db).get_user_by_id(current_user.id)


@api_router.get("/{user_id}", response_model=Union[UserReadWithEmail, UserRead])
async def get_user(
    user_id: uuid.UUID,
    db=Depends(get_async_session),
    current_user: User = Depends(current_user),
):
    user = await UsersCRUD(db).get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if current_user.is_superuser:
        return UserReadWithEmail.model_validate(user)
    return UserRead.model_validate(user)


@api_router.get("", response_model=List[Union[UserRead, UserReadWithEmail]])
async def get_users(
    search: str = None,
    page: int = Query(1, ge=1),
    order_by: Literal["last_name", "birth_date"] = "last_name",
    order: Literal["asc", "desc"] = "asc",
    superusers_to_top: bool = False,
    only_superusers: bool = False,
    filter_role: UserRole = None,
    db=Depends(get_async_session),
    current_user: User = Depends(optional_current_user),
):
    users = await UsersCRUD(db).get_users(
        order_by=order_by,
        order=order,
        search=search,
        page=page,
        superusers_to_top=superusers_to_top,
        only_superusers=only_superusers,
        filter_role=filter_role,
    )
    if current_user and current_user.is_superuser:
        return TypeAdapter(List[UserReadWithEmail]).validate_python(users)
    return TypeAdapter(List[UserRead]).validate_python(users)


@api_router.delete(
    "/{user_id}", status_code=204, dependencies=[Depends(current_superuser)]
)
async def delete_user(
    user_id: uuid.UUID,
    db=Depends(get_async_session),
):
    users_crud = UsersCRUD(db)
    user = await users_crud.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    await users_crud.delete(user)


@api_router.get(
    "/{user_id}/typed_tasks/completed", response_model=list[TypedTaskReadFull]
)
async def get_user_completed_typed_tasks(
    user_id: uuid.UUID,
    period_id: uuid.UUID = Query(...),
    db=Depends(get_async_session),
    current_db_user: User = Depends(current_user),
):
    user = await UsersCRUD(db).get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.id != current_db_user.id and not current_db_user.is_superuser:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    periods_crud = PeriodsCRUD(db)
    period = await periods_crud.get_period_by_id(period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Период не найден")
    return await TasksCRUD(db).get_user_completed_typed_tasks(
        user_id=user_id,
        period_start=period.period_start,
        period_end=period.period_end,
    )
