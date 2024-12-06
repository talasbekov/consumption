from datetime import timedelta, datetime

from fastapi import HTTPException, status, Depends
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session

from core import configs
from exceptions import BadRequestException
from models import User
from schemas import LoginForm, RegistrationForm, UserCreate
from services import user_service

from utils import hash_password, verify_password, is_valid_phone_number


class AuthService:

    def login(self, form: LoginForm, db: Session, Authorize: AuthJWT):
        user = user_service.get_by_email(db, EmailStr(form.email).lower())
        if not user or not verify_password(form.password, user.password):
            raise BadRequestException(detail="Incorrect email or password!")

        self._set_last_signed_at(db, user)
        access_token, refresh_token = self._generate_tokens(db, Authorize, user)
        return {"access_token": access_token, "refresh_token": refresh_token}

    def register(self, db: Session, form: RegistrationForm):
        if user_service.get_by_email(db, EmailStr(form.email).lower()):
            raise BadRequestException(
                detail="Пользователь с таким Email-ом уже существует!"
            )
        if user_service.get_by_iin(db, form.iin):
            raise BadRequestException(
                detail="Пользователь с таким ИИН-ом уже существует!"
            )
        if not is_valid_phone_number(form.phone_number):
            raise BadRequestException(
                detail="Неправильно ввели телефонный номер! Попробуйте через +7"
            )
        if form.password != form.re_password:
            raise BadRequestException(detail="Ваши пороли не совпадают!")

        user_obj_in = UserCreate(
            email=EmailStr(form.email).lower(),
            name=form.name,
            password=hash_password(form.password),
        )
        print(user_obj_in, "user_obj_in")
        user = user_service.create(db=db, obj_in=user_obj_in)
        print(user)
        return user

    def refresh_token(self, db: Session, Authorize: AuthJWT):
        if not Authorize.get_jwt_subject():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not refresh access token",
            )
        user = user_service.get(db, Authorize.get_jwt_subject())
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The user belonging to this token no longer exist",
            )

        access_token, refresh_token = self._generate_tokens(db, Authorize, user)

        return {"access_token": access_token, "refresh_token": refresh_token}

    def _generate_tokens(self, db: Session, Authorize: AuthJWT, user: User):

        # Определение дополнительных утверждений для токена
        user_claims = {
            "email": str(user.email),
            "employee_id": str(user.employee_id) if user.employee_id else "",
        }

        # Создание токена доступа
        access_token = Authorize.create_access_token(
            subject=str(user.id),
            user_claims=user_claims,
            expires_time=timedelta(minutes=configs.ACCESS_TOKEN_EXPIRES_IN),
        )

        # Создание токена обновления
        refresh_token = Authorize.create_refresh_token(
            subject=str(user.id),
            user_claims=user_claims,
            expires_time=timedelta(minutes=configs.REFRESH_TOKEN_EXPIRES_IN),
        )

        return access_token, refresh_token

    def _set_last_signed_at(self, db: Session, user: User):
        user.last_signed_at = datetime.now()

        db.add(user)
        db.flush()

    # Зависимость для аутентификации и получения данных пользователя
    def get_current_user(self, Authorize: AuthJWT = Depends()):
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
        user_email = Authorize.get_raw_jwt()["email"]
        print(user_email)
        return {"user_id": user_id, "user_email": user_email}


auth_service = AuthService()
