from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.service import ai_service
from src.auth.dependencies import get_current_user_id
from src.database.dao.roomDAO import RoomDao
from src.database.deps import get_async_session
from src.database.models.rooms_models import RoomStatus

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
GetTokenData = Annotated[int, Depends(get_current_user_id)]

router = APIRouter(prefix="/rooms", tags="Rooms")

@router.post("/create_room", status_code=status.HTTP_201_CREATED)
async def create_room(creator_id: GetTokenData, session: SessionDep):
    room_dao = RoomDao(session=session)
    await room_dao.add(creator_id)
    await session.commit()

@router.post("/start_pending", status_code=status.HTTP_201_CREATED)
async def start_pendings(topic: str, creator_id: GetTokenData, session: SessionDep):
    content = await ai_service.generate_quiz(topic=topic)

    room_dao = RoomDao(session=session)
    await room_dao.update(filter_by={"creator_id": creator_id, "status": RoomStatus.WAITING}, topic=topic, status=RoomStatus.PREPARATION,**content.model_dump())
    await session.commit()