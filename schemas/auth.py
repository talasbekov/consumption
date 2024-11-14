from typing import Optional
from pydantic import EmailStr, validator

from schemas import Model


class LoginForm(Model):
    email: EmailStr
    password: str


class RegistrationForm(Model):
    email: EmailStr
    name: Optional[str]
    workplace: Optional[str]
    iin: Optional[str]
    phone_number: Optional[str]
    admin: Optional[bool]
    password: str
    re_password: str


class UserRegistrationForm(RegistrationForm):
    iin: str
    phone_number: Optional[str]

    @validator("iin")
    def validate_iin(cls, v):
        if not v.isdigit():
            raise ValueError("iin must contain only digits")
        if len(v) != 12:
            raise ValueError("iin must be exactly 12 digits")
        return v
