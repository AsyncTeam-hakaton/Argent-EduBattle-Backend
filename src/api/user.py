from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.service import ai_service
from src.auth.dependencies import get_current_user_id
from src.database.dao.userDAO import UserDao
from src.database.deps import get_async_session
from src.schemas.user_schem import AskBody, AskResponse, UserData

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