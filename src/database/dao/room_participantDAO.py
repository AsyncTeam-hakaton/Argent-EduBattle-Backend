from src.database.dao.baseDAO import BaseDao
from src.database.models.rooms_models import RoomMatch


class RoomDao(BaseDao[RoomMatch]):
    model = RoomMatch