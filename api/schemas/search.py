from pydantic import BaseModel
from typing import Optional, Literal, Union
import uuid
from datetime import date
from api.schemas.users import Institute


class SearchTaskData(BaseModel):
    """Данные задачи в результатах поиска"""

    id: uuid.UUID
    name: str
    use_in_pgas: bool
    event_id: Optional[uuid.UUID] = None
    group_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class SearchEventData(BaseModel):
    """Данные мероприятия в результатах поиска"""

    id: uuid.UUID
    name: str
    date: date
    location: str
    task_id: uuid.UUID  # ID связанной задачи

    class Config:
        from_attributes = True


class SearchGroupData(BaseModel):
    """Данные группы мероприятий в результатах поиска"""

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    events_count: int

    class Config:
        from_attributes = True


class SearchUserData(BaseModel):
    """Данные пользователя в результатах поиска"""

    id: uuid.UUID
    first_name: str
    last_name: str
    group: str
    institute: Optional[Institute] = None

    class Config:
        from_attributes = True


class SearchResultItem(BaseModel):
    """Единый результат поиска с типом и данными"""

    type: Literal["task", "event", "group", "user"]
    data: Union[SearchTaskData, SearchEventData, SearchGroupData, SearchUserData]


class SearchResponse(BaseModel):
    """Ответ от поиска"""

    query: str
    results: list[SearchResultItem]
    total: int
