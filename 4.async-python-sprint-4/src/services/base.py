from typing import Any, Generic, List, Optional, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from db.db import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDB(Repository, Generic[ModelType,
                                       CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.id == id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_by_short_url(self, db: AsyncSession,
                               short_url: Any) -> Optional[ModelType]:
        statement = select(self._model).where(
            self._model.short_url == short_url)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_many(
        self, db: AsyncSession, user_id: int, skip=0, limit=100
    ) -> List[ModelType]:
        statement = select(self._model).where(
            self._model.user == user_id).offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create(self, db: AsyncSession, *,
                     obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        short_url: str
    ) -> ModelType:
        statement = select(self._model).where(
            self._model.short_url == short_url)
        result = await db.execute(statement=statement)
        entity = result.scalar_one_or_none()
        entity.clicks += 1
        await db.commit()
        await db.refresh(entity)
        return entity

    async def update_type(self, db: AsyncSession,
                          url_id: int, tpe: str) -> ModelType:
        statement = select(self._model).where(self._model.id == url_id)
        result = await db.execute(statement=statement)
        entity = result.scalar_one_or_none()
        entity.type = tpe
        await db.commit()
        await db.refresh(entity)
        return entity

    async def delete(self, db: AsyncSession, url_id: int) -> ModelType:
        statement = select(self._model).where(self._model.id == url_id)
        result = await db.execute(statement=statement)
        entity = result.scalar_one_or_none()
        entity.is_deleted = True
        await db.commit()
        await db.refresh(entity)
        return entity


class UserDB(Repository, Generic[ModelType,
                                 CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(self, db: AsyncSession, login: str) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.login == login)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def create(self, db: AsyncSession, *,
                     obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
