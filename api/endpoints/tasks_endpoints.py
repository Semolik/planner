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


@api_router.put('/typed-tasks/{typed_task_id}/user/{user_id}', dependencies=[Depends(current_superuser)], status_code=204)
async def update_typed_task_state(
    typed_task_id: uuid.UUID,
    user_id: uuid.UUID,
    data: UpdateTypedTaskState,
    db=Depends(get_async_session)
):
    task_crud = TasksCRUD(db)
    users_crud = UsersCRUD(db)
    typed_task = await task_crud.get_typed_task(typed_task_id)
    if typed_task is None:
        raise HTTPException(
            status_code=404, detail="Типизированная задача не найдена")
    user = await users_crud.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if not user.is_superuser and typed_task.task_type not in user.roles:
        raise HTTPException(
            status_code=400, detail=f"У пользователя нет статуса {typed_task.task_type}")
    if data.period_start >= data.period_end:
        raise HTTPException(
            status_code=400, detail="Время начала должно быть раньше времени окончания")
    task_state = await task_crud.get_task_state(typed_task=typed_task, user=user)
    if not task_state is not None:
        await task_crud.assign_user_to_task(typed_task=typed_task, user=user, period_start=data.period_start, period_end=data.period_end, comment=data.comment, is_completed=data.is_completed)
    else:
        await task_crud.update_task_state(task_state=task_state, period_start=data.period_start, period_end=data.period_end, comment=data.comment, is_completed=data.is_completed)
    return


@api_router.delete('/typed-tasks/{typed_task_id}/user/{user_id}', status_code=204)
async def delete_typed_task_state(
    typed_task_id: uuid.UUID,
    user_id: uuid.UUID,
    db=Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    task_crud = TasksCRUD(db)
    users_crud = UsersCRUD(db)
    typed_task = await task_crud.get_typed_task(typed_task_id)
    if typed_task is None:
        raise HTTPException(
            status_code=404, detail="Типизированная задача не найдена")
    user = await users_crud.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    task_state = await task_crud.get_task_state(typed_task=typed_task, user=user)
    if task_state is None:
        raise HTTPException(
            status_code=404, detail="Задача не найдена")
    if not user.is_superuser and current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    await task_crud.delete(task_state)
    return


@api_router.get('/typed-tasks/{typed_task_id}', response_model=TypedTaskReadFull)
async def get_typed_task(typed_task_id: uuid.UUID, current_user: User = Depends(current_active_user), db=Depends(get_async_session)):
    task_crud = TasksCRUD(db)
    typed_task = await task_crud.get_typed_task(typed_task_id)
    if typed_task is None:
        raise HTTPException(
            status_code=404, detail="Типизированная задача не найдена")
    return typed_task


@api_router.get('/token', response_model=dict[UserRole, uuid.UUID], dependencies=[Depends(current_superuser)])
async def get_tasks_token(db=Depends(get_async_session)):
    tokens = await TasksCRUD(db).get_tasks_tokens()
    return {token.role: uuid.UUID(token.token) for token in tokens}


@api_router.put('/token', response_model=uuid.UUID, dependencies=[Depends(current_superuser)])
async def set_tasks_token(role: UserRole, db=Depends(get_async_session)):
    token = uuid.uuid4()
    await TasksCRUD(db).set_tasks_token(role=role, token=str(token))
    return token
