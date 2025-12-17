from datetime import date
from typing import Annotated, Literal, Union
from api.utilities.files import save_file, save_image
from api.schemas.events import CreateTypedTask, TaskCreate, TaskRead, TypedTaskReadFull
import uuid
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, Query
from api.cruds.tasks_crud import TasksCRUD
from api.cruds.users_crud import UsersCRUD
from api.core.users_controller import (
    current_superuser,
    optional_current_user,
    current_user,
)
from api.db.session import get_async_session
from api.models.user_models import User, UserRole
from api.schemas.files import File, ImageInfo

api_router = APIRouter(prefix="/tasks", tags=["tasks"])


@api_router.get("", response_model=list[TaskRead])
async def get_tasks(
    page: int = 1,
    hide_busy_tasks: bool = True,
    prioritize_unassigned: bool = True,
    current_user: User = Depends(optional_current_user),
    token: Annotated[Union[str, None], Header()] = None,
    db=Depends(get_async_session),
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
        prioritize_unassigned=prioritize_unassigned,
    )
    return tasks


@api_router.get("/my", response_model=list[TaskRead])
async def get_my_tasks(
    page: int = 1,
    current_user: User = Depends(current_user),
    db=Depends(get_async_session),
    filter: Literal["all", "active"] = "active",
):
    return await TasksCRUD(db).get_my_tasks(
        user_id=current_user.id, filter=filter, page=page
    )


@api_router.get(
    "/token",
    response_model=dict[UserRole, uuid.UUID],
    dependencies=[Depends(current_superuser)],
)
async def get_tasks_token(db=Depends(get_async_session)):
    tokens = await TasksCRUD(db).get_tasks_tokens()
    return {token.role: uuid.UUID(token.token) for token in tokens}


@api_router.put(
    "/token", response_model=uuid.UUID, dependencies=[Depends(current_superuser)]
)
async def set_tasks_token(role: UserRole, db=Depends(get_async_session)):
    token = uuid.uuid4()
    await TasksCRUD(db).set_tasks_token(role=role, token=str(token))
    return token


@api_router.get(
    "/{task_id}", response_model=TaskRead, dependencies=[Depends(current_user)]
)
async def get_task_by_id(task_id: uuid.UUID, db=Depends(get_async_session)):
    task = await TasksCRUD(db).get_task_by_id(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@api_router.post(
    "/{task_id}/typed-tasks",
    dependencies=[Depends(current_superuser)],
    status_code=201,
    response_model=TypedTaskReadFull,
)
async def create_typed_task(
    task_id: uuid.UUID, data: CreateTypedTask, db=Depends(get_async_session)
):
    task = await TasksCRUD(db).get_task_by_id(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if data.task_type in [typed_task.task_type for typed_task in task.typed_tasks]:
        raise HTTPException(
            status_code=400,
            detail=f"Типизированная задача с типом {data.task_type} уже существует для этой задачи",
        )
    typed_task = await TasksCRUD(db).create_typed_task(
        task_id=task.id,
        task_type=data.task_type,
        description=data.description,
        link=data.link,
        due_date=data.due_date,
        for_single_user=data.for_single_user,
    )
    return await TasksCRUD(db).get_typed_task(typed_task_id=typed_task.id)


@api_router.delete(
    "/{task_id}", dependencies=[Depends(current_superuser)], status_code=204
)
async def delete_task(task_id: uuid.UUID, db=Depends(get_async_session)):
    task = await TasksCRUD(db).get_task_by_id(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await TasksCRUD(db).delete(task)


@api_router.post(
    "",
    dependencies=[Depends(current_superuser)],
    status_code=201,
    response_model=TaskRead,
)
async def create_task(data: TaskCreate, db=Depends(get_async_session)):
    task = await TasksCRUD(db).create_task(
        name=data.name,
        event_id=None,
        use_in_pgas=data.use_in_pgas,
    )
    for role, typed_task_data in data.typed_tasks.items():
        if typed_task_data is not None:
            await TasksCRUD(db).create_typed_task(
                task_id=task.id,
                task_type=role,
                description=typed_task_data.description,
                link=typed_task_data.link,
                due_date=typed_task_data.due_date,
                for_single_user=typed_task_data.for_single_user,
            )
    return await TasksCRUD(db).get_task_by_id(task_id=task.id)
@api_router.post(
    "/birthday/{user_id}",
    dependencies=[Depends(current_superuser)],
    status_code=201,
    response_model=TaskRead,
)
async def create_birthday_task(user_id: uuid.UUID, due_date: date = Query(...), db=Depends(get_async_session)):
    user = await UsersCRUD(db).get_user_by_id(user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    task = await TasksCRUD(db).create_task(
        name=None,
        event_id=None,
        use_in_pgas=True,
        birthday_user_id=user_id
    )
    await TasksCRUD(db).create_typed_task(
        task_id=task.id,
        task_type=UserRole.COPYWRITER,
        due_date=due_date,
        for_single_user=True,
    )
    await TasksCRUD(db).create_typed_task(
        task_id=task.id,
        task_type=UserRole.DESIGNER,
        due_date=due_date,
        for_single_user=True,
    )
    return await TasksCRUD(db).get_task_by_id(task_id=task.id)

@api_router.post(
    "/{task_id}/files",
    dependencies=[Depends(current_superuser)],
    status_code=201,
    response_model=File,
)
async def upload_file_to_task(
    task_id: uuid.UUID, file: UploadFile, db=Depends(get_async_session)
):
    task = await TasksCRUD(db).get_task_by_id(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_file = await save_file(db=db, upload_file=file)
    await TasksCRUD(db).add_file_to_task(task_id=task.id, file_id=db_file.id)
    return db_file


@api_router.post(
    "/{task_id}/images",
    dependencies=[Depends(current_superuser)],
    status_code=201,
    response_model=ImageInfo,
)
async def upload_image_to_task(
    task_id: uuid.UUID, image: UploadFile, db=Depends(get_async_session)
):
    task = await TasksCRUD(db).get_task_by_id(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_image = await save_image(
        db=db,
        upload_file=image,
    )
    await TasksCRUD(db).add_image_to_task(task_id=task.id, image_id=db_image.id)
    return db_image


@api_router.delete(
    "/{task_id}/images/{image_id}",
    dependencies=[Depends(current_superuser)],
    status_code=204,
)
async def delete_image_from_task(
    task_id: uuid.UUID, image_id: uuid.UUID, db=Depends(get_async_session)
):
    task = await TasksCRUD(db).get_task_by_id(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task_image = await TasksCRUD(db).get_task_image(task_id=task.id, image_id=image_id)
    if task_image is None:
        raise HTTPException(status_code=404, detail="Image not found in task")
    await TasksCRUD(db).delete(task_image)


@api_router.delete(
    "/{task_id}/files/{file_id}",
    dependencies=[Depends(current_superuser)],
    status_code=204,
)
async def delete_file_from_task(
    task_id: uuid.UUID, file_id: uuid.UUID, db=Depends(get_async_session)
):
    task = await TasksCRUD(db).get_task_by_id(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task_file = await TasksCRUD(db).get_task_file(task_id=task.id, file_id=file_id)
    if task_file is None:
        raise HTTPException(status_code=404, detail="File not found in task")
    await TasksCRUD(db).delete(task_file)


