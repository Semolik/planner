from fastapi import APIRouter, Depends, Query
from api.db.session import get_async_session
from api.cruds.search_crud import SearchCRUD
from api.schemas.events import (
    TaskReadShort,
    EventReadShort,
    EventGroupReadShort,
    TaskRead,
    EventRead,
)
from api.schemas.search import (
    SearchResponse,
    SearchResultItem,
)
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas.users import UserReadShort

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, max_length=100, description="Поисковый запрос"),
    limit: int = Query(50, ge=1, le=100, description="Максимум результатов"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Поиск по задачам, мероприятиям, группам и пользователям

    - **q**: Поисковый запрос (минимум 1 символ)
    - **limit**: Максимум результатов для каждого типа (по умолчанию 50, максимум 100)
    """
    search_crud = SearchCRUD(session)
    results = await search_crud.search(query=q, limit=limit)

    # Формируем единый список результатов
    search_results: list[SearchResultItem] = []

    # Добавляем задачи
    for task in results["tasks"]:
        search_results.append(
            SearchResultItem(
                type="task", data=TaskRead.model_validate(task, from_attributes=True)
            )
        )

    # Добавляем мероприятия
    for event in results["events"]:
        search_results.append(
            SearchResultItem(
                type="event", data=EventRead.model_validate(event, from_attributes=True)
            )
        )

    # Добавляем группы мероприятий
    for group in results["groups"]:
        search_results.append(
            SearchResultItem(
                type="group",
                data=EventGroupReadShort.model_validate(group, from_attributes=True),
            )
        )

    # Добавляем пользователей
    for user in results["users"]:
        search_results.append(
            SearchResultItem(
                type="user",
                data=UserReadShort.model_validate(user, from_attributes=True),
            )
        )

    return SearchResponse(
        query=q,
        results=search_results,
        total=len(search_results),
    )
