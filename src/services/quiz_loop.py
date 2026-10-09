import asyncio
import logging

from pydantic import TypeAdapter
from sqlalchemy.exc import SQLAlchemyError

from src.database.base import async_session_factory
from src.database.dao.roomDAO import RoomDao
from src.database.models.rooms_models import RoomStatus
from src.redis.match import MatchService
from src.redis.redis import get_redis
from src.schemas.ai_shem import Question
from src.services.ws_manager import manager

logger = logging.getLogger(__name__)

questions_adapter = TypeAdapter(list[Question])

async def run_quiz_loop(room_id: int):
    async with async_session_factory() as session:
        room_dao = RoomDao(session=session)
        room = await room_dao.find_one_or_none(room_id = room_id, status = RoomStatus.ACTIVE)

        if not room or not room.quiz_questions:
            return

        questions: list[Question] = questions_adapter.validate_python(room.quiz_questions)

    for index, q in enumerate(questions):
        await manager.broadcast(
            room_id=room_id,
            message={
                "event": "NEXT_QUESTIONS",
                "payload": {
                    "index_q": index + 1,
                    "title": q.title,
                    "options": q.options,
                }
            }
            )
        await asyncio.sleep(20)

    try:
        match_service = MatchService(redis=get_redis())
        final = await match_service.finalize_match(room_id=room_id)

        async with async_session_factory() as session:
            room_dao = RoomDao(session=session)
            await room_dao.update(filter_by={"id": room_id}, status = RoomStatus.FINISHED)
            await session.commit()

        await manager.broadcast(room_id=room_id, message=final)

    except SQLAlchemyError as e:
        logger.error("Ошибка при сохранении результатов комнаты %s в БД: %s", room_id, e)
        return {
        "event": "FINAL_QUIZ_MATCH_DON'T_FINALIZED",
        "payload": {
            "room_id": room_id,
            }
        }