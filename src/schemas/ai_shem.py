from pydantic import BaseModel, Field


class Question(BaseModel):
    title: str = Field(description="Текст вопроса")
    options: list[str] = Field(description="Ровно 4 варианта ответа")
    correct_idx: int = Field(description="Индекс правильного ответа (0-3)")
    explanation: str = Field(description="Краткое объяснение ответа")

class LectureBlock(BaseModel):
    title: str = Field(description="Заголовок подраздела текста")
    content: str = Field(description="Понятный учебный текст (2-4 абзаца)")

class Lecture(BaseModel):
    topic_title: str = Field(description="Главная тема лекции")
    summary: str = Field(description="Краткий вводный тезис")
    blocks: list[LectureBlock] = Field(description="3-4 логических раздела")

class RoomFullContent(BaseModel):
    lecture: Lecture

    qualification_questions: list[Question] = Field(
        description="4 простых вопроса по материалу лекции для проверки прочтения(допуск)"
    )

    quiz_questions: list[Question] = Field(
        description="7-10 продвинутых/сложных вопросов по теме(приоритет по материалу лекции). Не дублировать вопросы из квалификации!"
    )

class ask_result(BaseModel):
    response: str = Field(description="текст ответа")