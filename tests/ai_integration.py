import pytest

from src.ai.service import ai_service
from src.schemas.ai_shem import RoomFullContent


@pytest.mark.asyncio
async def test_live_gen_room_content():

    from src.config import settings
    print(f"\n[DEBUG] BASE_URL = '{settings.AI_BASE_URL}'")
    print(f"[DEBUG] MODEL = '{settings.AI_MODEL}'")

    topic = "Основы Docker и контейнеризации"

    result: RoomFullContent = await ai_service.generate_quiz(topic=topic)

    assert isinstance(result, RoomFullContent)

    assert result.lecture.topic_title != ""
    assert len(result.lecture.blocks) >= 3
    for block in result.lecture.blocks:
        assert block.title != ""
        assert block.content != ""

    assert len(result.qualification_questions) == 4
    for q in result.qualification_questions:
        assert len(q.options) == 4
        assert 0 <= q.correct_idx <= 3
        assert q.title != ""
        assert q.explanation != ""

    assert 7 <= len(result.quiz_questions) <= 10
    for q in result.quiz_questions:
        assert len(q.options) == 4
        assert 0 <= q.correct_idx <= 3
        assert q.title != ""
        assert q.explanation != ""

    print("\n\nУспешно сгенерировано!")
    print(f"Главная тема: {result.lecture.topic_title}")
    print(f"Первый вопрос допуска: {result.qualification_questions[0].title}")
    print(f"Варианты: {result.qualification_questions[0].options}")
    print(f"Правильный индекс: {result.qualification_questions[0].correct_idx}")