from sqlalchemy import or_, select

from src.database.dao.baseDAO import BaseDao
from src.database.models.rooms_models import RoomMatch


class RoomMatchDao(BaseDao[RoomMatch]):
    model = RoomMatch

    async def get_user_score(self, room_id: int, user_id: int) -> RoomMatch | None:
        stmt = (
            select(RoomMatch)
            .where(
                RoomMatch.room_id == room_id,
                or_(RoomMatch.player1_id == user_id, RoomMatch.player2_id == user_id),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_room_matches(
            self,
            room_id: int,
            pairs: list[tuple[int, int]]
    ) -> list[RoomMatch]:
        pairs_list = [
            RoomMatch(
                room_id=room_id,
                player1_id=p1,
                player2_id=p2,
                player1_score=0,
                player2_score=0,
            )
            for p1, p2 in pairs
        ]
        self.session.add_all(pairs_list)
        await self.session.flush()
        return pairs_list

    async def save_final_scores(
            self,
            room_id: int,
            final_scores: dict[int, int]
    ) -> None:
        matches = await self.find_all(room_id=room_id)

        for match in matches:
            match.player1_score = final_scores.get(match.player1_id, 0)
            match.player2_score = final_scores.get(match.player2_id, 0)

        await self.session.flush()