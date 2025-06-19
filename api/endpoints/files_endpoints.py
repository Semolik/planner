from cruds.file_cruds import FilesCRUD
import uuid
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import FileResponse
from utilities.files import get_file_path, get_image_path
from db.session import get_async_session

api_router = APIRouter(tags=["files"])


@api_router.get("/images/{image_id}", response_class=FileResponse)
async def get_app_image(
    image_id: uuid.UUID = Path(...),
    db=Depends(get_async_session),
):
    files_crud = FilesCRUD(db)
    image = await files_crud.get_image_by_id(image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    return FileResponse(get_image_path(image=image))


@api_router.get("/files/{file_id}", response_class=FileResponse)
async def get_app_image(
    file_id: uuid.UUID = Path(...),
    db=Depends(get_async_session),
):
    files_crud = FilesCRUD(db)
    file = await files_crud.get_file_by_id(file_id=file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    return FileResponse(get_file_path(file=file), filename=file.file_name)
