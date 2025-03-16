from datetime import datetime
import uuid

from sqlalchemy.orm import selectinload

from cruds.base_crud import BaseCRUD
from models.user import User, UserRole
from models.events import Task, TypedTask, TaskState
from sqlalchemy import select, and_, or_
from sqlalchemy.sql import exists


class TasksCRUD(BaseCRUD):
    async def create_task(self, name: str, due_date: datetime | None = None, event_id: uuid.UUID | None = None) -> Task:
        task = Task(
            name=name,
            event_id=event_id,
            due_date=due_date,
        )
        return await self.create(task)

    async def get_typed_task(self, typed_task_id: uuid.UUID) -> TypedTask:
        query = select(TypedTask).where(TypedTask.id == typed_task_id).options(
            selectinload(TypedTask.users), selectinload(TypedTask.task_states), selectinload(TypedTask.parent_task).selectinload(Task.event))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def assign_user_to_task(self, typed_task: TypedTask, user: User) -> TaskState:
        task_state = TaskState(
            type_task_id=typed_task.id,
            user_id=user.id,
        )
        await self.create(task_state)
        return task_state

    async def is_user_assigned_to_task(self, typed_task: TypedTask, user: User) -> bool:
        query = select(TaskState).where(TaskState.type_task_id ==
                                        typed_task.id, TaskState.user_id == user.id)
        result = await self.db.execute(query)
        return result.scalars().first() is not None

    async def create_typed_task(self, task_id: uuid.UUID, task_type: UserRole,  for_single_user: bool, description: str | None = None) -> TypedTask:
        typed_task = TypedTask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            for_single_user=for_single_user,
        )
        return await self.create(typed_task)

    async def get_task(self, task_id: uuid.UUID) -> Task:
        query = select(Task).where(Task.id == task_id).options(
            selectinload(Task.typed_tasks))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_full_task(self, task_id: uuid.UUID) -> Task:
        query = select(Task).where(Task.id == task_id).options(
            selectinload(Task.typed_tasks).selectinload(TypedTask.users))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_tasks(self, page: int, per_page: int = 10) -> list[Task]:
        query = select(Task).slice((page - 1) * per_page, page * per_page)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_tasks(self, task_types: list[UserRole]) -> list[tuple[Task,
                                                                        TypedTask]]:
        typed_task_subquery = (
            select(TypedTask.task_id)
            .where(TypedTask.task_type.in_(task_types))
            .distinct()
            .scalar_subquery()
        )

        query = (
            select(Task, TypedTask)
            .join(Task.typed_tasks)
            .where(Task.id.in_(typed_task_subquery))
            .group_by(Task.id)
            .having(
                or_(
                    # Для задач с for_single_user = True проверяем, что никто не назначен
                    and_(
                        TypedTask.for_single_user == True,
                        ~exists().where(
                            TaskState.type_task_id == TypedTask.id,
                            TaskState.user_id.isnot(None),
                        ),
                    ),
                    # Для задач с for_single_user = False разрешаем любые назначения
                    TypedTask.for_single_user == False,
                )
            )
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_user_open_tasks(self, user_id: uuid.UUID, task_types: list[UserRole]) -> list[tuple[Task, TypedTask]]:
        query = select(Task, TypedTask).join(TypedTask, Task.id == TypedTask.task_id).join(
            TaskState, TypedTask.id == TaskState.type_task_id).where(
            TaskState.is_completed == False, TypedTask.task_type.in_(task_types), TaskState.user_id == user_id)
        result = await self.db.execute(query)
        return result.all()
