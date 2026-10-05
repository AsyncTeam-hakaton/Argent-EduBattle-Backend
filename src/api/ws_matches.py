import random
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from redis import Redis
from src.auth.dependencies import get_current_user_id
from src.auth.security import decode_access_token
from src.database.base import async_session_factory
from src.database.dao.room_matchDAO import RoomMatchDao
from src.database.dao.room_participantDAO import RoomParticipanDAO
from src.database.dao.roomDAO import RoomDao
from src.database.deps import get_async_session
from src.database.models.rooms_models import ParticipantStatus, RoomStatus
from src.redis.match import MatchService
from src.redis.redis import get_redis
from src.schemas.match import MatchPair, ProcessAnswer, StartMatchRequest
from src.services.ws_manager import manager

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
GetTokenData = Annotated[int, Depends(get_current_user_id)]
RedisDep = Annotated[Redis, Depends(get_redis)]

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.websocket("/ws/quiz/{room_id}")
async def proc_ans(
    websocket: WebSocket,
    room_id: int,
    token: str,
):
    token_data =  decode_access_token(token=token)
    if not token_data or token_data.user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = token_data.user_id

    try:
        async with async_session_factory() as session:
            room_parti_dao = RoomParticipanDAO(session=session)
            await room_parti_dao.update(filter_by={"user_id": user_id}, status = ParticipantStatus.APPROVED)
            await session.commit()
    except SQLAlchemyError:
        await websocket.close(code=1011, reason="Failed to update student status")
        return

    await manager.connect(room_id=room_id, user_id=user_id, websocket=websocket)

    try:
        redis = get_redis()
        redis_manager = MatchService(redis=redis)
        while True:
            payload = await websocket.receive_json()

            answer_data = ProcessAnswer(
                room_id=room_id,
                user_id=user_id,
                question_id=payload["question_id"],
                is_correct=payload["is_correct"]
            )

            result = await redis_manager.process_answer(answer_data=answer_data)

            await manager.send_personal_message(room_id=room_id, user_id=user_id, message=result)
        
    except WebSocketDisconnect:
        manager.disconnect(room_id=room_id, user_id=user_id)


@router.post("/init_quiz", status_code=status.HTTP_201_CREATED)
async def init_redis_hash_table(creator_id: GetTokenData, session: SessionDep, redis: RedisDep):
    room_parti_dao = RoomParticipanDAO(session=session)
    room_dao = RoomDao(session=session)
    room_match_dao = RoomMatchDao(session=session)
    redis_service = MatchService(redis=redis)

    room = await room_dao.find_one_or_none(creator_id=creator_id, status = RoomStatus.PREPARATION)
    if not room:
        raise HTTPException(status_code=404, detail="Комната в режиме подготовки не найдена")
    
    participants = await room_parti_dao.find_all(room_id = room.id, status= ParticipantStatus.APPROVED)

    user_ids = [p.user_id for p in participants]
    if len(user_ids) < 2:
        raise HTTPException(status_code=400, detail="Нужно хотя бы 2 одобренных участника для старта")
    random.shuffle(user_ids)

    pairs: list[tuple[int, int]] = [
        (user_ids[i], user_ids[i+1])
        for i in range(0, len(user_ids)-1, 2)
    ]

    await room_match_dao.create_room_matches(room_id=room.id, pairs=pairs)

    match_init_schem = StartMatchRequest(
        room_id=room.id,
        pairs=[
            MatchPair(player1_id=p1, player2_id=p2)
            for p1, p2 in pairs
        ]
    )
    await redis_service.init_match(match_data=match_init_schem)

    await manager.broadcast(
        room_id=room.id,
        message={
            "event": "MATCH_STARTED",
            "payload": {
                "room_id": room.id,
                "message": "Матч начался, готовимся к первому вопросу!"
            }
        }
    )   
    await room_dao.update(filter_by={"id": room.id}, status = RoomStatus.ACTIVE)
    await session.commit()
