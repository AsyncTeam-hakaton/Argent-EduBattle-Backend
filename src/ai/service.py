from src.ai.client import ai_client
from src.ai.prompts import SYSTEM_QUIZ_GENERATOR_PROMPT
from src.config import settings
from src.schemas.ai_shem import RoomFullContent


class AIService:
    def __init__(self):
        self.client = ai_client
        self.model = settings.AI_MODEL


    async def generate_quiz(self, topic: str) -> RoomFullContent:
        response = await self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_QUIZ_GENERATOR_PROMPT},
                {"role": "user", "content": f"Тема для комнаты: {topic}"},
            ],
            response_format=RoomFullContent,
        )
        return response.choices[0].message.parsed

ai_service = AIService()