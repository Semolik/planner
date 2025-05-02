from datetime import time
from typing import Annotated, Union
from schemas.events import TypedTaskRead, TypedTaskReadFull, TaskRead, UpdateTypedTaskState
import uuid
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from cruds.tasks_crud import TasksCRUD
from cruds.users_crud import UsersCRUD
from users_controller import current_superuser, current_active_user, optional_current_user
from db.session import get_async_session
from models.user import User, UserRole

api_router = APIRouter(prefix="/tasks", tags=["tasks"])


@api_router.get('', response_model=list[TaskRead])
async def get_tasks(
    page: int = 1,
    hide_busy_tasks: bool = True,
    prioritize_unassigned: bool = True,
    current_user: User = Depends(optional_current_user),
    token: Annotated[Union[str, None], Header()] = None,
    db=Depends(get_async_session)
):
    if current_user is None:
        if token is None:
            raise HTTPException(status_code=401, detail="Токен не передан")
        db_token = await TasksCRUD(db).get_tasks_token_by_token(token=token)
        if db_token is None:
            raise HTTPException(status_code=401, detail="Неверный токен")
        roles = [db_token.role]
    else:
        user = await UsersCRUD(db).get_user_by_id(current_user.id)
        roles = user.roles
    tasks = await TasksCRUD(db).get_tasks(
        page=page,
        user_id=current_user.id if current_user is not None else None,
        roles=roles,
        hide_busy_tasks=hide_busy_tasks,
        prioritize_unassigned=prioritize_unassigned
    )
    return tasks


@api_router.get('/token', response_model=dict[UserRole, uuid.UUID], dependencies=[Depends(current_superuser)])
async def get_tasks_token(db=Depends(get_async_session)):
    tokens = await TasksCRUD(db).get_tasks_tokens()
    return {token.role: uuid.UUID(token.token) for token in tokens}


@api_router.put('/token', response_model=uuid.UUID, dependencies=[Depends(current_superuser)])
async def set_tasks_token(role: UserRole, db=Depends(get_async_session)):
    token = uuid.uuid4()
    await TasksCRUD(db).set_tasks_token(role=role, token=str(token))
    return token
