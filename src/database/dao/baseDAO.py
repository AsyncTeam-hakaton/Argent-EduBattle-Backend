from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseDao(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_id(self, model_id: Any) -> ModelType | None:
        return await self.session.get(self.model, model_id)


    async def find_one_or_none(self, **filter_by) -> ModelType | None:
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def find_all(self, **filter_by) -> Sequence[ModelType]:
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def add(self, **data) -> ModelType:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        return instance


    async def update(self, filter_by: dict, **data) -> None:
        stmt = update(self.model).filter_by(**filter_by).values(**data)
        await self.session.execute(stmt)


    async def delete(self, **filter_by) -> None:
        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)