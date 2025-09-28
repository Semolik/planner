from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from cruds.institutes_crud import InstitutesCRUD
from schemas.users import Institute, InstituteCreateOrEdit
from core.users_controller import current_superuser
from db.session import get_async_session


api_router = APIRouter(prefix="/institutes", tags=["institutes"])


@api_router.post(
    "", response_model=Institute, dependencies=[Depends(current_superuser)]
)
async def create_institute(
    institute: InstituteCreateOrEdit,
    db=Depends(get_async_session),
):
    institutes_crud = InstitutesCRUD(db)
    if await institutes_crud.get_institute_by_name(institute.name):
        raise HTTPException(
            status_code=400, detail="Институт с таким названием уже существует"
        )
    return await institutes_crud.create_institute(name=institute.name)


@api_router.put(
    "/{institute_id}",
    response_model=Institute,
    dependencies=[Depends(current_superuser)],
)
async def update_institute(
    institute: InstituteCreateOrEdit,
    institute_id: uuid.UUID,
    db=Depends(get_async_session),
):
    institutes_crud = InstitutesCRUD(db)
    db_institute = await institutes_crud.get_institute_by_id(institute_id)
    if db_institute is None:
        raise HTTPException(status_code=404, detail="Институт не найден")
    return await institutes_crud.update_institute(
        institute=db_institute, name=institute.name
    )


@api_router.get("", response_model=List[Institute])
async def get_institutes(
    db=Depends(get_async_session),
):
    institutes_crud = InstitutesCRUD(db)
    return await institutes_crud.get_institutes()


@api_router.get("/{institute_id}", response_model=Institute)
async def get_institute(
    institute_id: uuid.UUID,
    db=Depends(get_async_session),
):
    institutes_crud = InstitutesCRUD(db)
    institute = await institutes_crud.get_institute_by_id(institute_id)
    if institute is None:
        raise HTTPException(status_code=404, detail="Институт не найден")
    return institute


@api_router.delete(
    "/{institute_id}", status_code=204, dependencies=[Depends(current_superuser)]
)
async def delete_institute(institute_id: uuid.UUID, db=Depends(get_async_session)):
    institutes_crud = InstitutesCRUD(db)
    institute = await institutes_crud.get_institute_by_id(institute_id)
    if institute is None:
        raise HTTPException(status_code=404, detail="Институт не найден")
    if await institutes_crud.has_connected_users(institute):
        raise HTTPException(
            status_code=400, detail="Институт имеет привязанных пользователей"
        )
    await institutes_crud.delete(institute)
