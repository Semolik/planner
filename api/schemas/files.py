from typing import Any, Annotated

from fastapi import Query
from pydantic import (
    BaseModel,
    model_validator,
    validator,
    BeforeValidator,
    PlainSerializer,
)
from api.utilities.files import get_file_link, get_image_link
from api.models.files_models import Image
from uuid import UUID


def validate_image_link(v: Any) -> str | None:
    if not v:
        return None
    if isinstance(v, str):  # уже строка
        return v
    if not isinstance(v, Image):
        raise TypeError("ImageLink must be Image (model)")
    return get_image_link(image_id=v.id)


ImageLink = Annotated[
    str | None,
    BeforeValidator(validate_image_link),
    PlainSerializer(lambda x: x, return_type=str, when_used="always"),
]


class ImageInfo(BaseModel):
    id: UUID
    url: str = None

    @validator("url", pre=True, always=True)
    def set_url(cls, url, values, **kwargs):
        if url is not None:
            return url
        return get_image_link(values["id"])

    class Config:
        from_attributes = True


class File(BaseModel):
    id: UUID
    url: str = None
    file_name: str = Query(
        ..., description="Имя файла, как оно было на компьютере пользователя"
    )

    @model_validator(mode="after")
    def url_generator(self) -> "File":
        self.url = get_file_link(file_id=self.id)
        return self

    class Config:
        from_attributes = True
