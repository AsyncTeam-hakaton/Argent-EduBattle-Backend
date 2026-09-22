import logging

from redis.asyncio import Redis

from src.schemas.match import StartMatchRequest

logger = logging.getLogger(__name__)

class MatchService:
    def __init__(self, redis: Redis, default_ttl: int = 7200):
        self.redis = redis
        self.default_ttl = default_ttl

    async def _get_pairs_key(self, room_id: int) -> str:
        return f"match:{room_id}:pairs"

    async def _get_scores_key(self, room_id: int) -> str:
        return f"match:{room_id}:scores"

    async def init_match(self, match_data: StartMatchRequest) -> None:
        pairs_key = self._get_pairs_key(match_data.room_id)
        scores_key = self._get_scores_key(match_data.room_id)

        pairs_dict: dict[str, str] = {}
        scores_dict: dict[str, str] = {}

        for pair in match_data.pairs:
            p1_str = str(pair.player1_id)
            p2_str = str(pair.player2_id)

            pairs_dict[p1_str] = p2_str
            pairs_dict[p2_str] = p1_str

            scores_dict[p1_str] = 0
            scores_dict[p2_str] = 0

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.hset(pairs_key, mapping=pairs_dict)
            pipe.hset(scores_key, mapping=scores_dict)
            pipe.expire(pairs_key, self.default_ttl)
            pipe.expire(scores_key, self.default_ttl)
            await pipe.execute()

        logger.info("🎮 Матч для комнаты %s успешно инициализирован в Redis.", match_data.room_id)

    async def add_score(self, room_id: int, user_id: int, points: int = 1) -> int:
        scores_key = self._get_scoresfff_key(room_id)
        return await self.redis.hincrby(scores_key, str(user_id), points)

    async def get_opponent_id(self, room_id: int, user_id: int) -> int | None:
        pairs_key = self._get_pairs_key(room_id)
        opponent_id = await self.redis.hget(pairs_key, str(user_id))
        return int(opponent_id) if opponent_id else None 
        