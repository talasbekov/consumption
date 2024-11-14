from datetime import datetime
from typing import Optional
from pydantic import EmailStr, validator

from schemas import ReadNamedModel, NamedModel


class UserBase(NamedModel):
    name: Optional[str]
    email: Optional[EmailStr]
    workplace: Optional[str]
    admin: Optional[bool]
    iin: int
    phone_number: Optional[str]
    last_signed_at: Optional[datetime]
    login_count: Optional[int]


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserRead(UserBase, ReadNamedModel):
    iin: int

    @validator("iin")
    def validate_iin(cls, v):
        if not v.isdigit():
            raise ValueError("iin must contain only digits")
        if len(v) != 12:
            raise ValueError("iin must be exactly 12 digits")
        return v
