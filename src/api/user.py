from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user_id
from src.database.dao.userDAO import UserDao
from src.database.deps import get_async_session
from src.schemas.user_schem import UserData

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
GetTokenData = Annotated[int, Depends(get_current_user_id)]

router = APIRouter(prefix="/users", tags=['Users'])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def add_user(user_data: UserData, session: SessionDep) -> None:
    user_dao = UserDao(session=session)
    await user_dao.add(**user_data.model_dump())
    await session.commit()
    
    