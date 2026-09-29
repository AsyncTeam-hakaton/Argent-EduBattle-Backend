from src.database.dao.baseDAO import BaseDao
from src.database.models.rooms_models import RoomParticipant


class RoomParticipanDAO(BaseDao[RoomParticipant]):
    model = RoomParticipant