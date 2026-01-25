from fastapi.staticfiles import StaticFiles
from api.utilities.vk import VKUtils
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from api.endpoints.settings_endpoints import api_router as settings_router
from api.endpoints.institutes_endpoints import api_router as institutes_router
from api.endpoints.files_endpoints import api_router as files_router
from api.endpoints.users_endpoints import api_router as users_router
from api.endpoints.auth_endpoints import api_router as auth_router
from api.endpoints.events_endpoints import api_router as events_router
from api.endpoints.required_periods import api_router as required_periods_router
from api.endpoints.tasks_endpoints import api_router as tasks_router
from api.endpoints.events_groups_endpoints import api_router as events_groups_router
from api.endpoints.events_levels import api_router as events_levels_router
from api.endpoints.typed_tasks_endpoints import api_router as typed_tasks_router
from api.endpoints.typed_tasks_states_endpoints import (
    api_router as typed_tasks_states_router,
)
from api.endpoints.calendar_endpoints import api_router as calendar_router
from api.endpoints.vk_endpoints import api_router as vk_router

from api.endpoints.home_endpoints import api_router as home_router
from api.endpoints.statistics_endpoints import api_router as statistics_router
from api.endpoints.search_endpoints import router as search_router
from api.endpoints.meetings_endpoints import api_router as meetings_router
from api.endpoints.custom_achievements_endpoints import (
    api_router as custom_achievements_router,
)

from api.db.session import async_session_maker
from contextlib import asynccontextmanager
from fastapi import FastAPI

from api import event_listener

from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)


app = FastAPI(docs_url=None, redoc_url=None)
app.mount(
    "/static",
    StaticFiles(directory=f"{'' if settings.DEV_MODE else 'api/'}static"),
    name="static",
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


app.include_router(auth_router)
app.include_router(home_router)
app.include_router(events_levels_router)
app.include_router(calendar_router)
app.include_router(events_router)
app.include_router(required_periods_router)
app.include_router(events_groups_router)
app.include_router(tasks_router)
app.include_router(typed_tasks_router)
app.include_router(typed_tasks_states_router)
app.include_router(users_router)
app.include_router(files_router)
app.include_router(vk_router)
app.include_router(institutes_router)
app.include_router(settings_router)
app.include_router(statistics_router)
app.include_router(search_router)
app.include_router(meetings_router)
app.include_router(custom_achievements_router)


main_app_lifespan = app.router.lifespan_context


@asynccontextmanager
async def lifespan_wrapper(app):
    try:
        async with async_session_maker() as session:
            vk_utils = VKUtils(session=session)
            token = await vk_utils.get_token()
            if token:
                await vk_utils.start_bot(token=token)
            app.state.vk_utils = vk_utils
            event_listener.add_vk_listeners(app.state.vk_utils)
    except Exception as exception:
        print(exception)
    async with main_app_lifespan(app) as maybe_state:
        yield maybe_state


# app.router.lifespan_context = lifespan_wrapper
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Set-Cookie"],
)
