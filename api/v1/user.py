# app/api/v1/user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core import get_db
from models import User
from schemas import UserRead, UserCreate, UserUpdate
from services import user_service

router = APIRouter(prefix="/api/v1/users2", tags=["users"])


@router.get(
    "",
    response_model=List[UserRead],
    summary="Получить всех пользователей (с пагинацией)"
)
async def get_all(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[User]:
    """
    Возвращает список пользователей, начиная с отступа `skip` и длиной `limit`.
    """
    users = await user_service.get_multi(db, skip, limit)
    return users


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Получить пользователя по ID"
)
async def get_one(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Возвращает одного пользователя по его ID.
    Если не найден — 404.
    """
    user = await user_service.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового пользователя"
)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Создаёт нового пользователя по Pydantic-схеме UserCreate.
    """
    new_user = await user_service.create(db, payload)
    return new_user


@router.put(
    "/{user_id}",
    response_model=UserRead,
    summary="Обновить пользователя"
)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Обновляет данные существующего пользователя. Если не найден — 404.
    """
    user = await user_service.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    updated_user = await user_service.update(db, user, payload)
    return updated_user


@router.delete(
    "/{user_id}",
    response_model=UserRead,
    summary="Удалить пользователя"
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Удаляет пользователя. Если не найден — 404.
    """
    user = await user_service.remove(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
