from fastapi import APIRouter, Depends, Query
from api.db.session import get_async_session
from api.cruds.search_crud import SearchCRUD
from api.schemas.search import SearchResponse, SearchResultItem, SearchTaskData, SearchEventData, SearchGroupData, SearchUserData
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, max_length=100, description="Поисковый запрос"),
    limit: int = Query(50, ge=1, le=100, description="Максимум результатов"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Поиск по задачам, мероприятиям, группам и пользователям

    - **q**: Поисковый запрос (минимум 2 символа)
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
                type="task",
                data=SearchTaskData(
                    id=task.id,
                    name=task.name,
                    use_in_pgas=task.use_in_pgas,
                    event_id=task.event_id,
                    group_id=None,  # Task не имеет прямой связи с группой, только через Event
                )
            )
        )

    # Добавляем мероприятия
    for event in results["events"]:
        search_results.append(
            SearchResultItem(
                type="event",
                data=SearchEventData(
                    id=event.id,
                    name=event.name,
                    date=event.date,
                    location=event.location,
                    task_id=event.task.id,
                )
            )
        )

    # Добавляем группы мероприятий
    for group in results["groups"]:
        search_results.append(
            SearchResultItem(
                type="group",
                data=SearchGroupData(
                    id=group.id,
                    name=group.name,
                    description=group.description,
                    events_count=len(group.events) if group.events else 0,
                )
            )
        )

    # Добавляем пользователей
    for user in results["users"]:
        search_results.append(
            SearchResultItem(
                type="user",
                data=SearchUserData(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    group=user.group,
                    institute=user.institute if hasattr(user, 'institute') else None,
                )
            )
        )

    return SearchResponse(
        query=q,
        results=search_results,
        total=len(search_results),
    )

