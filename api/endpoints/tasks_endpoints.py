from schemas.events import TypedTaskRead, TypedTaskReadFull
import uuid
from fastapi import APIRouter, Depends, HTTPException
from cruds.tasks_crud import TasksCRUD
from cruds.users_crud import UsersCRUD
from users_controller import current_superuser, current_active_user
from db.session import get_async_session
from models.user import User

api_router = APIRouter(prefix="/tasks", tags=["tasks"])


@api_router.post('/typed-task/{typed_task_id}/user/{user_id}', dependencies=[Depends(current_superuser)], status_code=204)
async def assign_user_to_task(typed_task_id: uuid.UUID, user_id: uuid.UUID, db=Depends(get_async_session)):
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
    if await task_crud.is_user_assigned_to_task(typed_task, user):
        raise HTTPException(
            status_code=400, detail="Пользователь уже назначен на эту задачу")
    return await task_crud.assign_user_to_task(typed_task, user)


@api_router.get('/typed-task/{typed_task_id}', response_model=TypedTaskReadFull)
async def assign_user_to_task(typed_task_id: uuid.UUID, current_user: User = Depends(current_active_user), db=Depends(get_async_session)):
    task_crud = TasksCRUD(db)
    typed_task = await task_crud.get_typed_task(typed_task_id)
    if typed_task is None:
        raise HTTPException(
            status_code=404, detail="Типизированная задача не найдена")
    return typed_task
