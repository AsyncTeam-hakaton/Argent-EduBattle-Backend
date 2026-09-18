from src.database.base import async_session_factory


async def get_async_session():
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise