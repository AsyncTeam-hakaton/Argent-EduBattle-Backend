from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.service import ai_service
from src.auth.dependencies import get_current_user_id
from src.database.dao.room_matchDAO import RoomMatchDao
from src.database.dao.roomDAO import RoomDao
from src.database.dao.userDAO import UserDao
from src.database.deps import get_async_session
from src.schemas.user_schem import (
    AskBody,
    AskResponse,
    PlayersPairs,
    RoomDetailedData,
    UserData,
)

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
GetTokenData = Annotated[int, Depends(get_current_user_id)]

router = APIRouter(prefix="/users", tags=['Users'])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def add_user(user_data: UserData, session: SessionDep) -> None:
    user_dao = UserDao(session=session)
    await user_dao.add(**user_data.model_dump())
    await session.commit()


@router.post("/ask_assist", response_model=AskResponse, status_code=status.HTTP_200_OK)
async def ask_ai(max_id: GetTokenData, ask_data: AskBody):
    res = await ai_service.ask_assistent(question=ask_data.question)
    if res is None:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Ассистент не отдал ответ")
    return AskResponse(max_id=max_id, response=res.response)


@router.get("/match_result/{room_id}", response_model=RoomDetailedData)
async def get_match_res(max_id: GetTokenData, session: SessionDep, room_id: int):
    room_dao = RoomDao(session=session)
    match_dao = RoomMatchDao(session=session)
    user_dao = UserDao(session=session)

    room = await room_dao.find_one_or_none(room_id = room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комната не найдена")
    
    teacher = await user_dao.find_one_or_none(max_id=room.creator_id)
    if teacher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден")

    pairs = await match_dao.find_all(room_id = room_id)

    pairs_list: list[PlayersPairs] = []
    for pair in pairs:
        p1_user = await user_dao.find_one_or_none(max_id = pair.player1_id)
        p2_user = await user_dao.find_one_or_none(max_id = pair.player2_id)

        pairs_list.append(PlayersPairs(
            player1_name=p1_user.name,
            player2_name=p2_user.name,
            player1_score=pair.player1_score,
            player2_score=pair.player2_score,
        ))

    room_data = RoomDetailedData(
        topic=room.topic,
        teacher_name=teacher.name,
        pairs=pairs_list,
    )
    return room_data


@router.get("/quiz_story")
async def get_quiz_story(max_id: GetTokenData, session: SessionDep):