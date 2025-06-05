import asyncio
from utilities.vk import VKUtils
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
app.include_router(users_router)
app.include_router(files_router)
app.include_router(institutes_router)
app.include_router(settings_router)


main_app_lifespan = app.router.lifespan_context


@asynccontextmanager
async def lifespan_wrapper(app):
    await create_db_and_tables()
    await init_db()

    async with main_app_lifespan(app) as maybe_state:
        yield maybe_state
    # loop = asyncio.get_event_loop()
    # await VKUtils().start_bot(loop)
app.router.lifespan_context = lifespan_wrapper
