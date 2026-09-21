import logging

from redis.asyncio import Redis, from_url

from src.config import settings

logger = logging.getLogger(__name__)

redis_client: Redis | None = None

async def init_redis() -> Redis:
    global redis_client
    if redis_client is None:
        redis_client = from_url(settings.REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info("🔌 Пул соединений Redis инициализирован.")
    return redis_client

async def get_redis() -> Redis:
    if redis_client is None:
        return await init_redis()
    return redis_client


async def close_redis() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None
        logger.info("🛑 Пул соединений Redis закрыт.")