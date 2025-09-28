from vkbottle import bold, italic
from models.user_models import User, UserRole
from cruds.events_crud import EventsCRUD
from models.events_models import Event
from db.session import AsyncSession
from datetime import datetime, timedelta

month_names = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
]


def get_user_name(user: User) -> str:
    """Получает имя пользователя в формате 'Имя Фамилия' или 'Имя Никнейм'."""
    name = f"{user.first_name} {user.last_name}"
    if user.vk_id:
        return f"[id{user.vk_id}|{name}]"

    return name


def format_event(event: Event, include_description=True, include_photographers=True):
    """Форматирует одно событие для вывода в сообщении."""
    message = bold(f"{event.name}\n")
    message += f"{event.date.day} {month_names[event.date.month - 1]} - {event.start_time.strftime('%H:%M')}\n"
    message += f"{event.location}\n"

    if include_description and event.description:
        message += f"\n{event.description}\n"

    if include_photographers:
        photographers_typed_task = next(
            (t for t in event.task.typed_tasks if t.task_type == UserRole.PHOTOGRAPHER),
            None,
        )
        if photographers_typed_task:
            users = [
                get_user_name(state.user)
                for state in photographers_typed_task.task_states
            ]
            if users:
                message += "\n" + ", ".join(users)

    message += "\n\n"
    return message


async def build_message(db: AsyncSession, role: UserRole) -> str:
    if role != UserRole.PHOTOGRAPHER:
        return "Роль не поддерживается для создания сообщения."

    events = await EventsCRUD(db).get_actual_events()
    now = datetime.now().date()

    # Флаги для контроля сокращений
    include_description = True
    include_photographers = True
    filtered_events = events[:]

    while True:
        message = italic("Актуальные мероприятия:\n\n")

        for event in filtered_events:
            message += format_event(
                event,
                include_description=include_description,
                include_photographers=include_photographers,
            )

        if message.length < 4096:
            return message

        # Шаг 1: Убрать описание мероприятий
        if include_description:
            include_description = False
            continue

        # Шаг 2: Исключить события старше двух недель
        two_weeks_later = now + timedelta(days=14)
        new_filtered_events = [e for e in filtered_events if e.date <= two_weeks_later]
        if len(new_filtered_events) < len(filtered_events):
            filtered_events = new_filtered_events
            continue

        # Шаг 3: Оставить только ближайшую неделю
        one_week_later = now + timedelta(days=7)
        new_filtered_events = [e for e in filtered_events if e.date <= one_week_later]
        if len(new_filtered_events) < len(filtered_events):
            filtered_events = new_filtered_events
            continue

        # Шаг 4: Убрать ФИО фотографов
        if include_photographers:
            include_photographers = False
            continue

        # Если всё уже минимально, но всё равно >4096 — обрезаем и предупреждаем
        if len(filtered_events) > 1:
            filtered_events.pop()
            continue

        return (
            "Сообщение слишком длинное даже после всех сокращений. "
            "Уточните диапазон дат или попробуйте позже."
        )
