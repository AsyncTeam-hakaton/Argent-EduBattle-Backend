from pydantic import BaseModel, Field

from database.models.users_models import UserRole


class UserData(BaseModel):
    max_id: int
    name: str = Field(max_length=64)
    role: UserRole

class  AskBody(BaseModel):
    question: str

class AskResponse(BaseModel):
    max_id: int
    response: str