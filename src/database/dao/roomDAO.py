from src.database.dao.baseDAO import BaseDao
from src.database.models.rooms_models import Room


class RoomDao(BaseDao[Room]):
    model = Room