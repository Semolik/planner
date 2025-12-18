from pydantic import BaseModel
from typing import  Literal, Union


from api.schemas.events import EventRead, EventGroupReadShort, TaskRead
from api.schemas.users import UserReadShort


class SearchResultItem(BaseModel):
    """Единый результат поиска с типом и данными"""

    type: Literal["task", "event", "group", "user"]
    data: Union[TaskRead, EventRead, EventGroupReadShort, UserReadShort]


class SearchResponse(BaseModel):
    """Ответ от поиска"""

    query: str
    results: list[SearchResultItem]
    total: int

