# app/services/base.py

from typing import Generic, Type, TypeVar, List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.exc import NoResultFound
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class ServiceBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, obj_id: Any) -> Optional[ModelType]:
        """
        Получить запись по первичному ключу.
        """
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Получить список записей с пагинацией.
        """
        stmt = select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, obj_in: CreateSchemaType
    ) -> ModelType:
        """
        Создать новую запись по Pydantic-схеме CreateSchemaType.
        """
        obj_data = obj_in.dict(exclude_unset=True)
        db_obj = self.model(**obj_data)  # type: ignore
        db.add(db_obj)
        await db.flush()      # чтобы сразу получить сгенерённые поля (например, id)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        Обновляет поля модели по Pydantic-схеме UpdateSchemaType.
        """
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def remove(self, db: AsyncSession, obj_id: Any) -> ModelType:
        """
        Удаляет запись по первичному ключу.
        """
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await db.execute(stmt)
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj  # type: ignore
