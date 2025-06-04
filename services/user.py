# app/services/user_service.py

from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sqlalchemy_update
from models import User
from schemas import UserCreate, UserUpdate
from services.base import ServiceBase


class UserService(ServiceBase[User, UserCreate, UserUpdate]):

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_iin(self, db: AsyncSession, iin: int) -> Optional[User]:
        stmt = select(User).where(User.iin == iin)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def user_login_activity(self, db: AsyncSession, user_id: int) -> None:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user:
            now = datetime.utcnow()
            if not user.last_login or now.date() > user.last_login.date():
                user.login_count = 1
            else:
                user.login_count += 1
            user.last_login = now
            db.add(user)
            await db.flush()

    async def get_login_count(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user and user.last_login and start_date <= user.last_login <= end_date:
            return user.login_count
        return 0


user_service = UserService(User)
