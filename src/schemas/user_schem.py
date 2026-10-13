from datetime import datetime

from pydantic import BaseModel, Field

from src.database.models.users_models import UserRole


class UserData(BaseModel):
    max_id: int
    name: str = Field(max_length=64)
    role: UserRole

class  AskBody(BaseModel):
    question: str

class AskResponse(BaseModel):
    max_id: int
    response: str

class PlayersPairs(BaseModel):
    player1_name: str
    player2_name: str
    player1_score: int
    player2_score: int

class RoomDetailedData(BaseModel):
    topic: str
    teacher_name: str
    pairs: list[PlayersPairs]

class RoomShortData(BaseModel):
    role: UserRole
    topic: str
    date: datetime
    score: int | None
    max_score: int | None
    len_students: int