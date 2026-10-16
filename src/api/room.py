from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.service import ai_service
from src.auth.dependencies import get_current_user_id
from src.database.dao.room_participantDAO import RoomParticipanDAO
from src.database.dao.roomDAO import RoomDao
from src.database.deps import get_async_session
from src.database.models.rooms_models import RoomStatus
from src.schemas.ai_shem import Lecture, Question, RoomFullContent
from src.schemas.room_schem import (
    LectureResponse,
    QualificationResponse,
    QuizResponse,
    RoomResponse,
    TopicResponse,
)

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
GetTokenData = Annotated[int, Depends(get_current_user_id)]

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.post("/create_room", status_code=status.HTTP_201_CREATED)
async def create_room(creator_id: GetTokenData, session: SessionDep):
    room_dao = RoomDao(session=session)
    room = await room_dao.add(creator_id=creator_id)
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


@router.post("/start_pending",response_model=RoomFullContent, status_code=status.HTTP_201_CREATED)
async def start_pendings(topic: str, creator_id: GetTokenData, session: SessionDep):
    content = await ai_service.generate_quiz(topic=topic)

    room_dao = RoomDao(session=session)
    await room_dao.update(filter_by={"creator_id": creator_id, "status": RoomStatus.WAITING}, topic=topic, status=RoomStatus.PREPARATION,**content.model_dump())
    await session.commit()

    return content


@router.get("/my_active_room", response_model=RoomResponse)
async def get_room_id(max_id: GetTokenData, session: SessionDep):
    room_dao = RoomDao(session=session)
    participant_dao = RoomParticipanDAO(session=session)

    role: str = "STUDENT"

    room_id = await participant_dao.search_active_room_of_user(user_id=max_id)
    if room_id is None:
        room_id = await room_dao.search_active_room_of_creator(creator_id=max_id)
        if room_id is None:
            raise HTTPException(404, "room not found")
        role = "CREATOR"
    
    return RoomResponse(room_id=room_id, your_role=role)


@router.get("/{room_id}/lecture", response_model=LectureResponse)
async def get_lecture(room_id: int, max_id: GetTokenData, session: SessionDep):
    room_dao = RoomDao(session=session)
    participant_dao = RoomParticipanDAO(session=session)

    room = await room_dao.find_one_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "room not found")

    if room.creator_id != max_id:
        is_member = await participant_dao.find_one_or_none(
            room_id=room_id, user_id=max_id
        )
        if is_member is None:
            raise HTTPException(403, "no access")

    return LectureResponse(room_id=room.id, lecture=room.lecture)


@router.get("/{room_id}/qualif_questions", response_model=QualificationResponse)
async def get_qualif_questions(room_id: int, max_id: GetTokenData, session: SessionDep):
    room_dao = RoomDao(session=session)
    participant_dao = RoomParticipanDAO(session=session)

    room = await room_dao.find_one_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "room not found")

    if room.creator_id != max_id:
        is_member = await participant_dao.find_one_or_none(
            room_id=room_id, user_id=max_id
        )
        if is_member is None:
            raise HTTPException(403, "no access")

    return QualificationResponse(room_id=room.id, qualification_questions=room.qualification_questions)


@router.get("/{room_id}/qualif_questions", response_model=QuizResponse)
async def get_quiz_questions(room_id: int, max_id: GetTokenData, session: SessionDep):
    room_dao = RoomDao(session=session)
    participant_dao = RoomParticipanDAO(session=session)

    room = await room_dao.find_one_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "room not found")

    if room.creator_id != max_id:
        is_member = await participant_dao.find_one_or_none(
            room_id=room_id, user_id=max_id
        )
        if is_member is None:
            raise HTTPException(403, "no access")

    return QuizResponse(room_id=room.id, quiz_questions=room.quiz_questions)


@router.get("/{room_id}/qualif_questions", response_model=TopicResponse)
async def get_topic(room_id: int, max_id: GetTokenData, session: SessionDep):
    room_dao = RoomDao(session=session)
    participant_dao = RoomParticipanDAO(session=session)

    room = await room_dao.find_one_or_none(id=room_id)
    if room is None:
        raise HTTPException(404, "room not found")

    if room.creator_id != max_id:
        is_member = await participant_dao.find_one_or_none(
            room_id=room_id, user_id=max_id
        )
        if is_member is None:
            raise HTTPException(403, "no access")

    return TopicResponse(room_id=room.id, topic=room.topic)


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

    update_questions_list = await room_dao.update_qualification_questions(room_id=room.id, questions=questions)
    
    await session.commit()
    return update_questions_list


