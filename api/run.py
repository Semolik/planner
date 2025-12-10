import uvicorn
import sys

sys.path.append("../")
from api.core.config import settings


def run():
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.API_PORT,
        reload=settings.DEV_MODE,
    )


if __name__ == "__main__":
    run()
