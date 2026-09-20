from openai import AsyncOpenAI

from src.config import settings

ai_client = AsyncOpenAI(
    api_key=settings.AI_API_KEY,
    base_url=settings.AI_BASE_URL,
    timeout=60.0
)