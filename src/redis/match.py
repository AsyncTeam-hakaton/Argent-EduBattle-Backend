import logging

from redis.asyncio import Redis

from src.schemas.match import ProcessAnswer, StartMatchRequest

logger = logging.getLogger(__name__)

class MatchService:
    def __init__(self, redis: Redis, default_ttl: int = 7200):
        self.redis = redis
        self.default_ttl = default_ttl

    async def _get_pairs_key(self, room_id: int) -> str:
        return f"match:{room_id}:pairs"

    async def _get_scores_key(self, room_id: int) -> str:
        return f"match:{room_id}:scores"

    def _get_question_pair_key(self, room_id: int, question_id: int, p1: int, p2: int) -> str:
        min_p, max_p = min(p1, p2), max(p1, p2)
        return f"room:{room_id}:q:{question_id}:pair:{min_p}:{max_p}"

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
        scores_key = self._get_scores_key(room_id)
        return await self.redis.hincrby(scores_key, str(user_id), points)

    async def get_opponent_id(self, room_id: int, user_id: int) -> int | None:
        pairs_key = self._get_pairs_key(room_id)
        opponent_id = await self.redis.hget(pairs_key, str(user_id))
        return int(opponent_id) if opponent_id else None 

    async def process_answer(
            self,
            answer_data: ProcessAnswer
    ) -> dict:

        opponent_id = await self.get_opponent_id(user_id=answer_data.user_id, room_id=answer_data.room_id)
        q_pair_key = self._get_question_pair_key(answer_data.room_id, answer_data.question_id, answer_data.user_id, opponent_id)

        is_closed = await self.redis.hget(q_pair_key, "is_closed")
        if is_closed:
            return {"event": "ROUND_ALREADY_CLOSED", "recipient_id": answer_data.user_id}

        user_has_answered = await self.redis.hget(q_pair_key, f"ans:{answer_data.user_id}")
        if user_has_answered:
            return {"event": "ALREADY_ANSWERED", "recipient_id": answer_data.user_id}

        await self.redis.hset(q_pair_key, f"ans:{answer_data.user_id}", "1")
        await self.redis.expire(q_pair_key, 120)

        if answer_data.is_correct:
            await self.redis.hset(q_pair_key, "is_closed", "1")
            await self.add_score(answer_data.room_id, answer_data.user_id)

            return {
            "event": "ROUND_FINISHED",
            "pair": [answer_data.user_id, opponent_id],
            "payload": {
                "question_id": answer_data.question_id,
                "winner_id": answer_data.user_id,
                "reason": "correct_answer"
            }
        }

        opp_has_answered = await self.redis.hget(q_pair_key, f"ans:{opponent_id}")
        if opp_has_answered:
            await self.redis.hset(q_pair_key, "is_closed", "1")
            return {
                "event": "ROUND_FINISHED",
                "pair": [answer_data.user_id, opponent_id],
                "payload": {
                    "question_id": answer_data.question_id,
                    "winner_id": None,
                    "reason": "both_incorrect"
                }
            }

        return {
        "event": "WAITING_OPPONENT_TURN",
        "pair": [answer_data.user_id, opponent_id],
        "payload": {
            "question_id": answer_data.question_id,
            "failed_user_id": answer_data.user_id
        }
    }