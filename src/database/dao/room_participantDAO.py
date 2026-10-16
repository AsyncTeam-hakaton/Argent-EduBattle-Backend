from sqlalchemy import func, select

from src.database.dao.baseDAO import BaseDao
from src.database.models.rooms_models import Room, RoomParticipant, RoomStatus


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

    async def search_active_room_of_user(self, user_id: int) -> int | None:
        stmt = (
            select(RoomParticipant.room_id)
            .join(Room, Room.id == RoomParticipant.room_id)
            .where(RoomParticipant.user_id == user_id, Room.status != RoomStatus.FINISHED)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()