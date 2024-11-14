from datetime import timedelta

from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core import configs
from services import user_service

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def get_access_token_by_user_id(Authorize: AuthJWT, db: Session, user_id: str):

    user = user_service.get_by_id(db, user_id)
    user_claims = {"role": bool(user.admin), "iin": str(user.iin)}
    access_token = Authorize.create_access_token(
        subject=str(user.id),
        user_claims=user_claims,
        expires_time=timedelta(minutes=configs.ACCESS_TOKEN_EXPIRES_IN),
    )
    return access_token
