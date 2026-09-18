from src.database.dao.baseDAO import BaseDao
from src.database.models.rooms_models import RoomParticipant


class RoomDao(BaseDao[RoomParticipant]):
    model = RoomParticipant