import asyncio
from utilities.vk import VKUtils
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from endpoints.settings_endpoints import api_router as settings_router
from endpoints.institutes_endpoints import api_router as institutes_router
from endpoints.files_endpoints import api_router as files_router
from endpoints.users_endpoints import api_router as users_router
from endpoints.auth_endpoints import api_router as auth_router
from endpoints.events_endpoints import api_router as events_router
from endpoints.tasks_endpoints import api_router as tasks_router
from endpoints.events_groups_endpoints import api_router as events_groups_router
from endpoints.events_levels import api_router as events_levels_router
from endpoints.typed_tasks_endpoints import api_router as typed_tasks_router
from endpoints.typed_tasks_states_endpoints import api_router as typed_tasks_states_router
from endpoints.vk_endpoints import api_router as vk_router
from db.session import async_session_maker
from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.init import init_db
import event_listener
from db.session import create_db_and_tables

app = FastAPI()

app.include_router(auth_router)
app.include_router(events_levels_router)
app.include_router(events_router)
app.include_router(events_groups_router)
app.include_router(tasks_router)
app.include_router(typed_tasks_router)
app.include_router(typed_tasks_states_router)
app.include_router(users_router)
app.include_router(files_router)
app.include_router(vk_router)
app.include_router(institutes_router)
app.include_router(settings_router)


main_app_lifespan = app.router.lifespan_context


@asynccontextmanager
async def lifespan_wrapper(app):
    await create_db_and_tables()
    await init_db()

    async with async_session_maker() as session:
        vk_utils = VKUtils(session=session)
        token = await vk_utils.get_token()
        if token:
            print("Starting VK bot ")

            await vk_utils.start_bot(token=token)
        app.state.vk_utils = vk_utils
    async with main_app_lifespan(app) as maybe_state:
        yield maybe_state

app.router.lifespan_context = lifespan_wrapper
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Set-Cookie"]
)
