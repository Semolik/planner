from utilities.files import save_file
from cruds.home_crud import HomeCRUD
from schemas.home import HomeNoteRead
from models.user_models import User, UserRole

import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.exceptions import HTTPException
from db.session import get_async_session
from core.users_controller import create_user, current_superuser, current_user
from schemas.files import File as FileSchema
import json
api_router = APIRouter(tags=["home"], prefix="/home")


@api_router.get("/notes", response_model=list[HomeNoteRead])
async def get_home_notes(
    db=Depends(get_async_session),
    current_user: User = Depends(current_user)
):
    """
    Получить заметки для главной страницы.
    """
    return await HomeCRUD(db).get_home_notes(
        roles=current_user.roles if not current_user.is_superuser else [
            UserRole[role.name] for role in UserRole]
    )


@api_router.post("/notes", response_model=HomeNoteRead, dependencies=[Depends(current_superuser)])
async def create_home_note(
    text: str = Form(...),
    role: UserRole = Form(...),
    db=Depends(get_async_session)
):
    exits_type_note = await HomeCRUD(db).get_note_by_type(role)
    if exits_type_note:
        raise HTTPException(
            status_code=400,
            detail=f"Заметка для роли {role} уже существует. Пожалуйста, обновите её."
        )
    note = await HomeCRUD(db).create_home_note(
        text=text,
        role=role
    )
    return await HomeCRUD(db).get_note_by_id(note.id)


@api_router.put("/notes/{note_id}", response_model=HomeNoteRead, dependencies=[Depends(current_superuser)])
async def update_home_note(
    note_id: uuid.UUID,
    text: str = Form(...),
    db=Depends(get_async_session)
):
    """
    Обновить заметку для главной страницы.
    """
    home_crud = HomeCRUD(db)
    note = await home_crud.get_note_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=404,
            detail="Заметка не найдена."
        )
    return await home_crud.update_note(
        note=note,
        text=text
    )


@api_router.post("/notes/{note_id}/files", dependencies=[Depends(current_superuser)], response_model=FileSchema)
async def add_file_to_home_note(
    note_id: uuid.UUID,
    file: UploadFile = File(...),
    db=Depends(get_async_session)
):

    home_crud = HomeCRUD(db)
    note = await home_crud.get_note_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=404,
            detail="Заметка не найдена."
        )

    db_file = await save_file(db=db, upload_file=file)
    await home_crud.add_file_to_note(
        note_id=note.id,
        file_id=db_file.id
    )
    return db_file


@api_router.delete("/notes/{note_id}", dependencies=[Depends(current_superuser)], status_code=204)
async def delete_home_note(
    note_id: uuid.UUID,
    db=Depends(get_async_session)
):
    """
    Удалить заметку для главной страницы.
    """
    home_crud = HomeCRUD(db)
    note = await home_crud.get_note_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=404,
            detail="Заметка не найдена."
        )
    await home_crud.delete(note)


@api_router.delete("/notes/{note_id}/files/{file_id}", dependencies=[Depends(current_superuser)], status_code=204)
async def delete_file_from_home_note(
    note_id: uuid.UUID,
    file_id: uuid.UUID,
    db=Depends(get_async_session)
):
    """
    Удалить файл из заметки для главной страницы.
    """
    home_crud = HomeCRUD(db)
    relation = await home_crud.get_note_file_relationship(
        note_id=note_id,
        file_id=file_id
    )
    if not relation:
        raise HTTPException(
            status_code=404,
            detail="Файл не найден в заметке."
        )
    await home_crud.delete(relation)
