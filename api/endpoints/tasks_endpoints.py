from datetime import time
from typing import Annotated, Union
from schemas.events import CreateTypedTask, TaskCreate, TaskRead, TypedTaskReadFull
import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from cruds.tasks_crud import TasksCRUD
from cruds.users_crud import UsersCRUD
from core.users_controller import current_superuser,  optional_current_user, current_user
from db.session import get_async_session
from models.user_models import User, UserRole

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


@api_router.get('/{task_id}', response_model=TaskRead, dependencies=[Depends(current_user)])
async def get_task_by_id(
    task_id: uuid.UUID,
    db=Depends(get_async_session)
):
    task = await TasksCRUD(db).get_task_by_id(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@api_router.post('/{task_id}/typed-tasks', dependencies=[Depends(current_superuser)], status_code=201, response_model=TypedTaskReadFull)
async def create_typed_task(
    task_id: uuid.UUID,
    data: CreateTypedTask,
    db=Depends(get_async_session)
):
    task = await TasksCRUD(db).get_task_by_id(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if data.task_type in [typed_task.task_type for typed_task in task.typed_tasks]:
        raise HTTPException(
            status_code=400, detail=f"Типизированная задача с типом {data.task_type} уже существует для этой задачи")
    typed_task = await TasksCRUD(db).create_typed_task(
        task_id=task.id,
        task_type=data.task_type,
        description=data.description,
        link=data.link,
        due_date=data.due_date,
        for_single_user=data.for_single_user
    )
    return await TasksCRUD(db).get_typed_task(typed_task_id=typed_task.id)


@api_router.delete('/{task_id}', dependencies=[Depends(current_superuser)], status_code=204)
async def delete_task(
    task_id: uuid.UUID,

    db=Depends(get_async_session)
):
    task = await TasksCRUD(db).get_task_by_id(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await TasksCRUD(db).delete(task)


@api_router.post('/', dependencies=[Depends(current_superuser)], status_code=201, response_model=TaskRead)
async def create_task(
    data: TaskCreate,
    db=Depends(get_async_session)
):
    task = await TasksCRUD(db).create_task(
        name=data.name,
        event_id=None,
    )
    for role, typed_task_data in data.typed_tasks.items():
        if typed_task_data is not None:
            await TasksCRUD(db).create_typed_task(
                task_id=task.id,
                task_type=role,
                description=typed_task_data.description,
                link=typed_task_data.link,
                due_date=typed_task_data.due_date,
                for_single_user=typed_task_data.for_single_user
            )
    return await TasksCRUD(db).get_task_by_id(task_id=task.id)
