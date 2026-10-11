from sqlalchemy import func, select

from src.database.dao.baseDAO import BaseDao
from src.database.models.rooms_models import RoomParticipant


class RoomParticipanDAO(BaseDao[RoomParticipant]):
    model = RoomParticipant

    async def count_participants_room(self, room_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(RoomParticipant)
            .where(RoomParticipant.room_id == room_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()