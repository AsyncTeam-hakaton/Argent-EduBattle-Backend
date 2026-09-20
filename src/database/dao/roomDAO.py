from typing import Any

from src.database.dao.baseDAO import BaseDao
from src.database.models.rooms_models import Room
from src.schemas.ai_shem import Lecture, Question, RoomFullContent


class RoomDao(BaseDao[Room]):
    model = Room

    async def save_ai_content(self, room_id: int, ai_content: RoomFullContent) -> Room | None:

        content_dict = ai_content.model_dump(mode="json")

        await self.update(
            filter_by={"id": room_id},
            lecture=content_dict["lecture"],
            qualification_questions=content_dict["qualification_questions"],
            quiz_questions=content_dict["quiz_questions"]
        )
        return await self.get_by_id(room_id)

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