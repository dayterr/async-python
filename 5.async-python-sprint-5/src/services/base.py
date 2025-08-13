from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from src.db.db import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class Repository(ABC):

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_many(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDB(Repository, Generic[ModelType,
                                       CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(self, db: AsyncSession, path: str) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.path == path)
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

    async def update(self, *args, **kwargs):
        pass

    async def delete(self, *args, **kwargs):
        pass

    async def get_by_params(self, db: AsyncSession, name=None, size=None, path=None,
                            skip=0, limit=100) -> List[ModelType]:

        statement = select(self._model).where(
            self._model.name == name
            and self._model.size == size
            and self._model.path == path).offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()


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
        return

    async def get_many(self, *args, **kwargs):
        pass

    async def update(self, *args, **kwargs):
        pass

    async def delete(self, *args, **kwargs):
        pass
