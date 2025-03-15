from models.events import Task
from schemas.events import EventFullInfo, EventCreateOrUpdate, TaskRead, TypedTaskRead
import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from cruds.events_crud import EventsCRUD
from cruds.tasks_crud import TasksCRUD
from cruds.users_crud import UsersCRUD
from users_controller import current_superuser
from db.session import get_async_session
from models.user import UserRole

api_router = APIRouter(prefix="/tasks", tags=["tasks"])


@api_router.post('/{typed_task_id}/user/{user_id}', response_model=TypedTaskRead, dependencies=[Depends(current_superuser)])
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
    if await task_crud.is_user_assigned_to_task(typed_task, user):
        raise HTTPException(
            status_code=400, detail="Пользователь уже назначен на эту задачу")
    return await task_crud.assign_user_to_task(typed_task, user)
