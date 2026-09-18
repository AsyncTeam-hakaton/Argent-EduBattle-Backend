from src.database.dao.baseDAO import BaseDao
from src.database.models.users_models import User


class UserDao(BaseDao[User]):
    model = User