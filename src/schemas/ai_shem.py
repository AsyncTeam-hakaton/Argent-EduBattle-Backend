from pydantic import BaseModel, Field


class GeneratedQuestion(BaseModel):
    title: str = Field(description="Текст вопроса")
    options: list[str] = Field(description="Ровно 4 варианта ответа")
    correct_idx: int = Field(description="Индекс правильного ответа (0-3)")
    explanation: str = Field(description="Краткое объяснение ответа")

class QuizResponse(BaseModel):
    topic: str
    questions: list[GeneratedQuestion]