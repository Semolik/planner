from schemas.events import CreateTypedTaskState, TypedTaskReadFull, TypedTaskState, UpdateTypedTaskState
import uuid
from fastapi import APIRouter, Depends, HTTPException
from cruds.tasks_crud import TasksCRUD
from cruds.users_crud import UsersCRUD
from core.users_controller import current_user
from db.session import get_async_session, AsyncSession
from models.user_models import User

api_router = APIRouter(prefix="/tasks/typed-tasks", tags=["typed tasks"])


async def validate_typed_task_state(
    typed_task_id: uuid.UUID,
    user: User,
    data: UpdateTypedTaskState,
    db: AsyncSession,
    current_user: User
):
    task_crud = TasksCRUD(db)
    typed_task = await task_crud.get_typed_task(typed_task_id)
    if typed_task is None:
        raise HTTPException(
            status_code=404, detail="Типизированная задача не найдена")
    if current_user.id != user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Нет доступа")
    if not user.is_superuser and typed_task.task_type not in user.roles:
        raise HTTPException(
            status_code=400, detail=f"У {'пользователя' if current_user.id != user.id else 'вас'} нет статуса {typed_task.task_type}")

    return typed_task


@api_router.post('/{typed_task_id}/user/{user_id}', status_code=201, response_model=TypedTaskState)
async def assign_user_to_task(
    typed_task_id: uuid.UUID,
    user_id: uuid.UUID,
    data: CreateTypedTaskState,
    db=Depends(get_async_session),
    current_user=Depends(current_user)
):
    users_crud = UsersCRUD(db)
    user = await users_crud.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    typed_task = await validate_typed_task_state(
        typed_task_id=typed_task_id,
        user=user,
        data=data,
        current_user=current_user,
        db=db
    )
    task_crud = TasksCRUD(db)
    task_state = await task_crud.get_task_state(typed_task=typed_task, user=user)
    if task_state:
        raise HTTPException(
            status_code=400, detail=f"{'Пользователь' if current_user.id != user.id else 'Вы'} уже зарегистрирован{'ы' if current_user.id == user.id else ''} на задачу")
    task_state = await task_crud.assign_user_to_task(
        typed_task=typed_task,
        user=user,
        comment=data.comment,
    )
    return await task_crud.get_task_state_by_id(
        typed_task_state_id=task_state.id
    )


@api_router.get('/{typed_task_id}', response_model=TypedTaskReadFull)
async def get_typed_task(typed_task_id: uuid.UUID, current_user: User = Depends(current_user), db=Depends(get_async_session)):
    task_crud = TasksCRUD(db)
    typed_task = await task_crud.get_typed_task(typed_task_id)
    if typed_task is None:
        raise HTTPException(
            status_code=404, detail="Типизированная задача не найдена")
    return typed_task
