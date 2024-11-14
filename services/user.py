from datetime import datetime
from sqlalchemy.orm import Session
from models import User  # Предполагается, что у вас есть модель User в models.py
from schemas import (
    UserCreate,
    UserUpdate,
)  # Предполагается, что у вас есть схемы создания и обновления событий
from services.base import ServiceBase


class UserService(ServiceBase[User, UserCreate, UserUpdate]):

    def get_by_email(self, db: Session, email: str):
        user = db.query(self.model).filter(self.model.email == email).first()
        return user

    def get_by_iin(self, db: Session, iin: int):
        user = db.query(self.model).filter(User.iin == iin).first()
        return user

    def user_login_activity(user_id: str, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            now = datetime.utcnow()
            if not user.last_login or now.date() > user.last_login.date():
                # Сброс счетчика, если последний логин был в другой день
                user.login_count = 1
            else:
                user.login_count += 1
            user.last_login = now
            db.commit()

    def get_login_count(
        user_id: str, start_date: datetime, end_date: datetime, db: Session
    ) -> int:
        user = db.query(User).filter(User.id == user_id).first()
        if user and start_date <= user.last_login <= end_date:
            return user.login_count
        return 0


user_service = UserService(User)
