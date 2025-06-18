from datetime import datetime, time
from typing import Literal, Optional
import uuid

from sqlalchemy.orm import selectinload, contains_eager

from cruds.base_crud import BaseCRUD
from models.user_models import User, UserRole
from models.events_models import Event, State, Task, TaskFile, TaskImage, TypedTask, TaskState, TasksToken, TaskStatePeriod
from sqlalchemy import select, and_, or_
from sqlalchemy.sql import exists
from sqlalchemy.sql import case


class TasksCRUD(BaseCRUD):
    async def create_task(self, name: str,  event_id: uuid.UUID | None = None) -> Task:
        task = Task(
            name=name,
            event_id=event_id,
        )
        return await self.create(task)

    def get_typed_task_options(self):
        return [selectinload(TypedTask.users),
                selectinload(TypedTask.task_states).selectinload(
                TaskState.user).options(selectinload(User.institute)),
                selectinload(TypedTask.parent_task).selectinload(Task.event).options(
                    selectinload(Event.group)
        ),
            selectinload(TypedTask.task_states).selectinload(TaskState.period)]

    async def get_typed_task(self, typed_task_id: uuid.UUID) -> TypedTask:
        query = select(TypedTask).where(TypedTask.id == typed_task_id).options(
            *self.get_typed_task_options()
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def assign_user_to_task(self, typed_task: TypedTask, user: User, comment: str) -> TaskState:
        task_state = TaskState(
            type_task_id=typed_task.id,
            user_id=user.id,

            comment=comment,
        )
        await self.create(task_state)
        return task_state

    async def get_task_state(self, typed_task: TypedTask, user: User) -> TaskState:
        query = select(TaskState).where(TaskState.type_task_id ==
                                        typed_task.id, TaskState.user_id == user.id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_task_state_by_id(self, typed_task_state_id: uuid.UUID) -> TaskState:
        query = select(TaskState).where(TaskState.id ==
                                        typed_task_state_id).options(
            selectinload(TaskState.user).options(selectinload(User.institute)),
            selectinload(TaskState.period),
            selectinload(TaskState.typed_task).selectinload(
                TypedTask.users).selectinload(User.roles_objects),
            selectinload(TaskState.typed_task).selectinload(
                TypedTask.parent_task).selectinload(Task.event).options(
                    selectinload(Event.group)
            ),
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_task_state_period_by_task_state_id(self, task_state_id: uuid.UUID) -> TaskStatePeriod:
        query = select(TaskStatePeriod).where(
            TaskStatePeriod.task_state_id == task_state_id).options(
            selectinload(TaskStatePeriod.task_state).selectinload(
                TaskState.user).options(selectinload(User.institute)),
            selectinload(TaskStatePeriod.task_state).selectinload(
                TaskState.period)

        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update_task_state(self, task_state: TaskState, comment: str, state: State) -> TaskState:

        task_state.comment = comment
        task_state.state = state
        return await self.update(task_state)

    async def create_typed_task(self, task_id: uuid.UUID, task_type: UserRole,  for_single_user: bool, due_date: datetime | None = None, description: str | None = None, link: str = "") -> TypedTask:
        typed_task = TypedTask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            due_date=due_date,
            link=link,
            for_single_user=for_single_user,
        )
        return await self.create(typed_task)

    async def update_typed_task(self, typed_task: TypedTask,  for_single_user: bool, due_date: datetime | None = None, description: str | None = None, link: str = "") -> TypedTask:
        typed_task.description = description
        typed_task.link = link
        typed_task.due_date = due_date
        typed_task.for_single_user = for_single_user
        return await self.update(typed_task)

    async def get_tasks(
        self,
        user_id: Optional[uuid.UUID] = None,
        roles: list[UserRole] = [],
        page: int = 1,
        per_page: int = 10,
        hide_busy_tasks: bool = True,
        prioritize_unassigned: bool = True
    ):
        if not roles:
            roles = [UserRole[role.name] for role in UserRole]

        if page < 1 or per_page < 1:
            raise ValueError("Page and per_page must be positive integers")

        current_datetime = datetime.now()

        # Подзапрос для проверки наличия исполнителей
        subquery_has_users = (
            exists()
            .where(
                and_(
                    TaskState.type_task_id == TypedTask.id,
                    TaskState.user_id.is_not(None),
                )
            )
            .correlate(TypedTask)
        )

        # Подзапрос для исключения прошедших мероприятий без фотографов
        past_events_without_photographers = (
            and_(
                TypedTask.task_type == UserRole.PHOTOGRAPHER,
                ~subquery_has_users,
                Task.event_id.is_not(None),
                Task.event.has(
                    or_(
                        Task.event.has(Event.date < current_datetime.date()),
                        and_(
                            Event.date <= current_datetime.date(),
                            Event.end_time <= current_datetime.time()
                        )
                    )
                )
            )
        )

        if prioritize_unassigned or not hide_busy_tasks:
            unassigned_query = self._get_unassigned_tasks_query(
                roles, subquery_has_users, user_id
            )
            # Исключаем прошедшие мероприятия без фотографов
            unassigned_query = unassigned_query.filter(
                ~past_events_without_photographers)
            result = await self.db.execute(unassigned_query)
            unassigned_tasks = result.unique().scalars().all()

            if len(unassigned_tasks) >= per_page:
                return unassigned_tasks[:per_page]

        if hide_busy_tasks and not user_id:
            regular_query = self._get_regular_tasks_query(
                roles, subquery_has_users
            )
        else:
            regular_query = self._get_all_tasks_query(roles, user_id)

        # Основной запрос
        regular_query = (
            select(Task)
            .join(TypedTask, TypedTask.task_id == Task.id)
            .where(TypedTask.task_type.in_(roles))
            .options(
                contains_eager(Task.typed_tasks).options(
                    selectinload(TypedTask.task_states).options(
                        selectinload(TaskState.user).options(
                            selectinload(User.institute)
                        ),
                        selectinload(TaskState.period)
                    ),
                    selectinload(TypedTask.users).options(
                        selectinload(User.roles_objects)
                    ),
                ),
                selectinload(Task.event).options(
                    selectinload(Event.group)
                ),
                selectinload(Task.files),
                selectinload(Task.images)
            )
        )

        # Сортируем так, чтобы задачи без исполнителей были первыми
        # Но исключаем прошедшие мероприятия без фотографов из приоритета
        if prioritize_unassigned:
            regular_query = regular_query.order_by(
                case(
                    (past_events_without_photographers, 2),  # Низкий приоритет
                    (subquery_has_users, 1),                # Средний приоритет
                    else_=0                                 # Высокий приоритет
                )
            )

        paginated_query = (
            regular_query
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        result = await self.db.execute(paginated_query)
        paginated_tasks = result.unique().scalars().all()

        return paginated_tasks

    def _get_unassigned_tasks_query(self, roles, subquery_has_users, user_id=None):
        query = (
            select(Task)
            .join(TypedTask, TypedTask.task_id == Task.id)
            .filter(
                TypedTask.task_type.in_(roles),
                ~subquery_has_users | (
                    TaskState.user_id == user_id if user_id else False)
            )
        )
        return query

    def _get_regular_tasks_query(self, roles, subquery_has_users):
        query = (
            select(Task)
            .join(TypedTask, TypedTask.task_id == Task.id)
            .filter(
                TypedTask.task_type.in_(roles),
                ~subquery_has_users
            )
        )
        return query

    def _get_all_tasks_query(self, roles, user_id=None):
        query = (
            select(Task)
            .join(TypedTask, TypedTask.task_id == Task.id)
            .filter(TypedTask.task_type.in_(roles))
        )
        if user_id:
            query = query.join(TaskState, TaskState.type_task_id == TypedTask.id).filter(
                TaskState.user_id == user_id)
        return query

    async def get_user_open_tasks(self, user_id: uuid.UUID, task_types: list[UserRole]) -> list[tuple[Task, TypedTask]]:
        query = select(Task, TypedTask).join(TypedTask, Task.id == TypedTask.task_id).join(
            TaskState, TypedTask.id == TaskState.type_task_id).where(
            TaskState.state == State.PENDING, TypedTask.task_type.in_(task_types), TaskState.user_id == user_id)
        result = await self.db.execute(query)
        return result.all()

    async def get_tasks_token(self, role: UserRole) -> TasksToken:
        query = select(TasksToken).where(TasksToken.role == role)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def set_tasks_token(self, role: UserRole, token: str) -> TasksToken:
        existing_token = await self.get_tasks_token(role)
        if existing_token:
            existing_token.token = token
            return await self.update(existing_token)
        else:
            tasks_token = TasksToken(role=role, token=token)
            return await self.create(tasks_token)

    async def get_tasks_token_by_token(self, token: str) -> TasksToken:
        query = select(TasksToken).where(TasksToken.token == token)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_tasks_tokens(self) -> list[TasksToken]:
        query = select(TasksToken)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_task_state_period(
            self, task_state_id: uuid.UUID, period_start: time, period_end: time) -> TaskStatePeriod:
        query = select(TaskStatePeriod).where(
            TaskStatePeriod.task_state_id == task_state_id)
        result = await self.db.execute(query)
        task_state_period = result.scalars().first()
        if not task_state_period:
            task_state_period = TaskStatePeriod(
                task_state_id=task_state_id,
                period_start=period_start,
                period_end=period_end
            )
            return await self.create(task_state_period)
        else:
            task_state_period.period_start = period_start
            task_state_period.period_end = period_end
            return await self.update(task_state_period)

    async def get_task_by_id(self, task_id: uuid.UUID) -> Task:
        query = select(Task).where(Task.id == task_id).options(
            selectinload(Task.event).options(
                selectinload(Event.group)
            ),
            selectinload(Task.typed_tasks).options(
                *self.get_typed_task_options()
            ),
            selectinload(Task.files),
            selectinload(Task.images)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def add_file_to_task(self, task_id: uuid.UUID, file_id: uuid.UUID) -> TaskFile:
        return await self.create(TaskFile(
            task_id=task_id,
            file_id=file_id
        ))

    async def add_image_to_task(self, task_id: uuid.UUID, image_id: uuid.UUID) -> TaskFile:
        return await self.create(TaskImage(
            task_id=task_id,
            image_id=image_id
        ))

    async def get_task_image(self, task_id: uuid.UUID, image_id: uuid.UUID) -> TaskImage:
        query = select(TaskImage).where(
            TaskImage.task_id == task_id, TaskImage.image_id == image_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_task_file(self, task_id: uuid.UUID, file_id: uuid.UUID) -> TaskFile:
        query = select(TaskFile).where(
            TaskFile.task_id == task_id, TaskFile.file_id == file_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_my_tasks(self, user_id: uuid.UUID, filter: Literal['all', 'active'] = 'active', page: int = 1, per_page: int = 10):

        query = (select(Task)
                 .join(TypedTask, TypedTask.task_id == Task.id)
                 .join(TaskState, TaskState.type_task_id == TypedTask.id))
        if filter == 'active':
            query = query.where(TaskState.state == State.PENDING)
        query = (
            query
            .where(TaskState.user_id == user_id)
            .options(
                contains_eager(Task.typed_tasks).options(
                    contains_eager(TypedTask.task_states).options(
                        selectinload(TaskState.user).options(
                            selectinload(User.institute)),
                        selectinload(TaskState.period)
                    ),
                    selectinload(TypedTask.users).options(
                        selectinload(User.roles_objects)),
                ),
                selectinload(Task.event).options(
                    selectinload(Event.group)
                ),
                selectinload(Task.files),
                selectinload(Task.images)
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        result = await self.db.execute(query)
        return result.unique().scalars().all()
