import io
import shutil
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, UploadFile
from pathlib import Path
from models.files_models import Image
from PIL import Image as PillowImage
from cruds.base_crud import BaseCRUD
from models.files_models import File

CONTENT_FOLDER = "/uploads"
IMAGES_FOLDER = "images"
FILES_FOLDER = "files"
IMAGES_EXTENSION = ".png"
SUPPORTED_IMAGE_EXTENSIONS = {
    ext
    for ext, fmt in PillowImage.registered_extensions().items()
    if fmt in PillowImage.OPEN
}


def get_image_path(image: Image) -> str:
    return f"{CONTENT_FOLDER}/{IMAGES_FOLDER}/{image.id}{IMAGES_EXTENSION}"


def get_image_link(image_id: UUID) -> str:
    return f"/api/images/{image_id}"


def get_file_link(file_id: UUID) -> str:
    return f"/api/files/{file_id}"


async def save_image(
    db: AsyncSession,
    upload_file: UploadFile,
    resize_image_options=(400, 400),
    detail_error_message="поврежденное изображение",
) -> Image:
    original_file_name = upload_file.filename
    original_file_path = Path(original_file_name)
    suffix = original_file_path.suffix.lower()

    if suffix not in SUPPORTED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=422, detail="Расширение изображения не поддерживается"
        )

    buf = io.BytesIO()
    buf.name = original_file_name
    shutil.copyfileobj(upload_file.file, buf)
    buf.seek(0)

    try:
        image = PillowImage.open(buf)
        image.thumbnail(resize_image_options)
        image_model = await BaseCRUD(db).create(Image())
        image_path = get_image_path(image=image_model)
        image.save(image_path)
        return image_model
    except Exception:
        raise HTTPException(status_code=422, detail=detail_error_message)


def get_file_path(file: File) -> str:
    return f"{CONTENT_FOLDER}/{FILES_FOLDER}/{file.id}"


async def save_file(db: AsyncSession, upload_file: UploadFile) -> File:
    content = await upload_file.read()

    original_file_name = upload_file.filename
    buf = io.BytesIO(content)
    buf.name = original_file_name

    file_model = await BaseCRUD(db).create(File(file_name=original_file_name))
    file_path = get_file_path(file=file_model)
    with open(file_path, "wb") as f:
        f.write(buf.read())
    return file_model
