from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.service import ai_service
from src.auth.dependencies import get_current_user_id
from src.database.dao.room_participantDAO import RoomParticipanDAO
from src.database.dao.roomDAO import RoomDao
from src.database.deps import get_async_session
from src.database.models.rooms_models import RoomStatus
from src.schemas.ai_shem import Lecture, Question

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
GetTokenData = Annotated[int, Depends(get_current_user_id)]

router = APIRouter(prefix="/rooms", tags="Rooms")

@router.post("/create_room", status_code=status.HTTP_201_CREATED)
async def create_room(creator_id: GetTokenData, session: SessionDep):
    room_dao = RoomDao(session=session)
    room = await room_dao.add(creator_id)
    await session.commit()

    return room


@router.post("/join_student", status_code=status.HTTP_201_CREATED)
async def join_student(max_id: GetTokenData, invite_code: str, session: SessionDep):
    room_dao = RoomDao(session=session)
    
    room_partic = RoomParticipanDAO(session=session)
    room = await room_dao.find_one_or_none(code=invite_code, status = RoomStatus.WAITING)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комната не найдена или подключение к ней недоступно"
        )
    
    participant = await room_partic.add(
        room_id = room.id,
        user_id = max_id,
    )

    await session.commit()
    return participant


@router.post("/start_pending", status_code=status.HTTP_201_CREATED)
async def start_pendings(topic: str, creator_id: GetTokenData, session: SessionDep):
    content = await ai_service.generate_quiz(topic=topic)

    room_dao = RoomDao(session=session)
    await room_dao.update(filter_by={"creator_id": creator_id, "status": RoomStatus.WAITING}, topic=topic, status=RoomStatus.PREPARATION,**content.model_dump())
    await session.commit()


@router.patch("/lecture", status_code=status.HTTP_200_OK)
async def edit_room_lecture(lecture: Lecture, creator_id: GetTokenData, session: SessionDep):
    room_dao = RoomDao(session=session)

    room = await room_dao.find_one_or_none(status = RoomStatus.PREPARATION, creator_id=creator_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Комната не найдена или у вас нет прав на её редактирование"
        )

    update_room = await room_dao.update_lecture(room_id=room.id, lecture=lecture)
    
    await session.commit()
    return update_room

@router.patch("/quiz_questions", status_code=status.HTTP_200_OK)
async def edit_quiz_questions(questions: list[Question], creator_id: GetTokenData, session: SessionDep):
    room_dao = RoomDao(session=session)

    room = await room_dao.find_one_or_none(status = RoomStatus.PREPARATION, creator_id=creator_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Комната не найдена или у вас нет прав на её редактирование"
        )

    update_questions_list = await room_dao.update_quiz_questions(room_id=room.id, questions=questions)
    
    await session.commit()
    return update_questions_list

@router.patch("/qualif_questions", status_code=status.HTTP_200_OK)
async def edit_qualif_questions(questions: list[Question], creator_id: GetTokenData, session: SessionDep):
    room_dao = RoomDao(session=session)

    room = await room_dao.find_one_or_none(status = RoomStatus.PREPARATION, creator_id=creator_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Комната не найдена или у вас нет прав на её редактирование"
        )

    update_questions_list = await room_dao.update_quiz_questions(room_id=room.id, questions=questions)
    
    await session.commit()
    return update_questions_list


