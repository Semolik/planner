import asyncio
import logging
import sys

from sqlalchemy.sql import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed


sys.path = ["", "..", *sys.path[1:]]
from api.db.init import init_db  # noqa
from api.db.session import async_session_maker  # noqa


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
)
async def init() -> None:
    try:
        db = async_session_maker()

        response = await db.execute(text("SELECT 1"))

        log_info = f"Response value {response.first()}"
        logger.info(log_info)
        await init_db(db)
        await db.close()
    except Exception as e:
        logger.exception("Failed to initialize database", exc_info=e)
        raise


async def main() -> None:
    logger.info("Ping DB")
    await init()
    logger.info("DB pong'ed")


if __name__ == "__main__":
    asyncio.run(main())
