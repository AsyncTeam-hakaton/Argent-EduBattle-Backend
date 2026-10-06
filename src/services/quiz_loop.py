import asyncio

from pydantic import TypeAdapter

from src.database.base import async_session_factory
from src.database.dao.roomDAO import RoomDao
from src.database.models.rooms_models import RoomStatus
from src.schemas.ai_shem import Question
from src.services.ws_manager import manager

questions_adapter = TypeAdapter(list[Question])

async def run_quiz_loop(room_id: int):
    async with async_session_factory() as session:
        room_dao = RoomDao(session=session)
        room = await room_dao.find_one_or_none(room_id = room_id, status = RoomStatus.ACTIVE)

        if not room or not room.questions:
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