from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class RegistrationForm(BaseModel):
    email: EmailStr
    password: constr(min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str  # обычно "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class UserRead(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True
