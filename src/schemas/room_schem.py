from pydantic import BaseModel

from src.schemas.ai_shem import Lecture, Question


class LectureResponse(BaseModel):
    room_id: int
    lecture: Lecture | None

class QualificationResponse(BaseModel):
    room_id: int
    qualification_questions: list[Question] | None

class QuizResponse(BaseModel):
    room_id: int
    quiz_questions: list[Question] | None

class TopicResponse(BaseModel):
    room_id: int
    topic: str | None

class RoomResponse(BaseModel):
    room_id: int
    your_role: str