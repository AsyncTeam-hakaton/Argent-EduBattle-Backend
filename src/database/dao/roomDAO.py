from collections.abc import Sequence
from typing import Any

from sqlalchemy import select

from src.database.dao.baseDAO import BaseDao
from src.database.models.rooms_models import Room, RoomParticipant, RoomStatus
from src.schemas.ai_shem import Lecture, Question


class RoomDao(BaseDao[Room]):
    model = Room

    async def find_users_rooms(self, user_id: int) -> Sequence[Room]:
        stmt = (
            select(Room)
            .join(RoomParticipant, RoomParticipant.room_id == Room.id)
            .where(Room.status == RoomStatus.FINISHED,
                   RoomParticipant.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_quiz_questions(
        self, 
        room_id: int, 
        questions: list[Question] | list[dict[str, Any]]
    ) -> Room | None:
        data = [
            q.model_dump(mode="json") if isinstance(q, Question) else q 
            for q in questions
        ]
        await self.update(filter_by={"id": room_id}, quiz_questions=data)
        return await self.get_by_id(room_id)

    async def update_qualification_questions(
        self, 
        room_id: int, 
        questions: list[Question] | list[dict[str, Any]]
    ) -> Room | None:
        data = [
            q.model_dump(mode="json") if isinstance(q, Question) else q 
            for q in questions
        ]
        await self.update(filter_by={"id": room_id}, qualification_questions=data)
        return await self.get_by_id(room_id)

    async def update_lecture(
        self, 
        room_id: int, 
        lecture: Lecture | dict[str, Any]
    ) -> Room | None:
        data = lecture.model_dump(mode="json") if isinstance(lecture, Lecture) else lecture
        await self.update(filter_by={"id": room_id}, lecture=data)
        return await self.get_by_id(room_id)