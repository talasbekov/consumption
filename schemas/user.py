from datetime import datetime
from typing import Optional
from pydantic import EmailStr

from schemas import ReadNamedModel, NamedModel


class UserBase(NamedModel):
    name: Optional[str]
    email: Optional[EmailStr]
    last_signed_at: Optional[datetime]
    login_count: Optional[int]


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserRead(UserBase, ReadNamedModel):
    pass
