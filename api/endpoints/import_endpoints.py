from datetime import datetime
from sqlalchemy import and_, or_, select
from cruds.events_crud import EventsCRUD
from models.user_models import User, UserRole
from cruds.institutes_crud import InstitutesCRUD
from cruds.file_cruds import FilesCRUD
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile
from fastapi.responses import FileResponse
from utilities.files import get_image_path
from db.session import get_async_session
from core.users_controller import create_user, current_superuser
import json
api_router = APIRouter(tags=["import"], prefix="/import")


@api_router.post("/users", status_code=204)
async def import_users(
    db=Depends(get_async_session),
    file: UploadFile = File(...)
):
    """
   json cодержит список пользователей для импорта.
    """
    if file.content_type != 'application/json':
        raise HTTPException(
            status_code=400, detail="Неверный формат файла. Ожидается JSON.")

    content = await file.read()
    try:
        users_data = content.decode('utf-8')
        users_data = json.loads(users_data)
        for user in users_data:
            found_user_query = select(User).where(
                User.first_name == user['first_name'],
                User.last_name == user['last_name'],
                User.patronymic == user['patronymic'],
            )
            found_user = await db.execute(found_user_query)
            found_user = found_user.scalars().first()
            if found_user:
                print(
                    f"Пользователь {user['first_name']} {user['last_name']} уже существует, пропускаем.")
                continue
            institute = await InstitutesCRUD(db).get_institute_by_name(
                name=user['institute_id'])
            if not institute:
                institute = await InstitutesCRUD(db).create_institute(
                    name=user['institute_id'])
            await create_user(
                first_name=user['first_name'],
                last_name=user['last_name'],
                patronymic=user['patronymic'],
                group=user.get('group', None),
                birth_date=user.get('birth_date', None),
                username=user.get('username', None),
                roles=[UserRole.PHOTOGRAPHER, UserRole.COPYWRITER],
                password=''.join(uuid.uuid4().hex.split('-')),
                phone=None,
                vk_id=None,
                institute_id=institute.id,
                is_superuser=False,

            )
            print(
                f"Пользователь {user['first_name']} {user['last_name']} успешно импортирован.")

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Ошибка при обработке файла: {str(e)}")


@api_router.post("/events", status_code=204)
async def import_events(
    db=Depends(get_async_session),
    file: UploadFile = File(...)
):
    """
    JSON содержит список мероприятий для импорта.
    """
    if file.content_type != 'application/json':
        raise HTTPException(
            status_code=400, detail="Неверный формат файла. Ожидается JSON.")

    content = await file.read()

    events_data = content.decode('utf-8')
    events_data = json.loads(events_data)
    for event in events_data:
        # Здесь должна быть логика импорта мероприятия
        # Например, проверка на существование, создание нового мероприятия и т.д.
        photographers = event.get('photographers', [])
        for photographer in photographers:
            part1, part2 = photographer.split(' ', 1)
            found_user_query = select(User).where(
                or_(
                    and_(User.first_name == part1,
                         User.last_name == part2),
                    and_(User.first_name == part2, User.last_name == part1)
                )
            )
            found_user = await db.execute(found_user_query)
            found_user = found_user.scalars().first()

            if not found_user:
                print(f"Пользователь {photographer} не найден, пропускаем.")
                pass
            level = await EventsCRUD(db).get_event_level_by_name(
                event.get('level_id', None))
            if not level:
                raise HTTPException(
                    status_code=404, detail=f"Уровень мероприятия {event.get('level_id', None)} не найден.")
            await EventsCRUD(db).create_event(
                name=event['name'],
                date=datetime.strptime(event['date'], '%Y-%m-%d').date(),
                name_approved=False,
                start_time=datetime.strptime(
                    event['start_time'], '%H:%M').time(),
                end_time=datetime.strptime(
                    event['end_time'], '%H:%M').time(),
                location=event['location'],
                organizer="",
                link=event.get('link', ''),
                required_photographers=len(photographers),
                description="",
                group_id=None,
                level_id=level.id
            )
