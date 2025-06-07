from schemas.events import CreateTypedTaskState, ReadTypedTaskState, TypedTaskReadFull, UpdateTypedTaskState
import uuid
from fastapi import APIRouter, Depends, HTTPException
from cruds.tasks_crud import TasksCRUD
from cruds.users_crud import UsersCRUD
from core.users_controller import current_superuser, current_user
from db.session import get_async_session, AsyncSession
from models.user_models import User

api_router = APIRouter(prefix="/tasks/typed-tasks/states",
                       tags=["typed tasks states"])


@api_router.put('/{typed_task_state_id}', response_model=ReadTypedTaskState)
async def update_user_typed_task_state(
    typed_task_state_id: uuid.UUID,
    data: UpdateTypedTaskState,
    db=Depends(get_async_session),
    current_user=Depends(current_user)
):
    task_crud = TasksCRUD(db)
    task_state = await task_crud.get_task_state_by_id(typed_task_state_id=typed_task_state_id)
    if not task_state:
        raise HTTPException(
            status_code=400, detail="Регистрация на задачу не найдена")
    if current_user.id != task_state.user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Нет доступа")
    task_state = await task_crud.update_task_state(task_state=task_state, comment=data.comment, is_completed=data.is_completed)


@api_router.delete('/{typed_task_state_id}', status_code=204)
async def delete_typed_task_state(
    typed_task_state_id: uuid.UUID,

    db=Depends(get_async_session),
    current_user: User = Depends(current_user)
):
    task_crud = TasksCRUD(db)
    task_state = await task_crud.get_task_state_by_id(typed_task_state_id=typed_task_state_id)
    if not task_state:
        raise HTTPException(
            status_code=400, detail="Регистрация на задачу не найдена")
    if current_user.id != task_state.user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Нет доступа")

    await task_crud.delete(task_state)
