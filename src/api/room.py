from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.service import ai_service
from src.auth.dependencies import get_current_user_id
from src.database.dao.roomDAO import RoomDao
from src.database.deps import get_async_session
from src.schemas.user_schem import AskBody, AskResponse, UserData