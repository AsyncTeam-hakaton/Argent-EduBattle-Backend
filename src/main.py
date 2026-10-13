import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.api.room import router as room_router
from src.api.user import router as user_router
from src.api.ws_matches import router as ws_match_router
from src.redis.redis import close_redis, init_redis

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    filemode='w'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting EduBattle Backend")
    await init_redis()

    yield
    logger.info("stopping EduBattle")
    await close_redis()

app = FastAPI(
    title="Argent EduBattle Api",
    description="Backend of EduBattle",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(room_router)
app.include_router(user_router)
app.include_router(ws_match_router)

@app.get("/")
async def root():
    return {
        "project": "EduBattle Backend",
        "status": "running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8888, reload=True)
