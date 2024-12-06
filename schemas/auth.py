from typing import Optional
from pydantic import EmailStr

from schemas import Model


class LoginForm(Model):
    email: EmailStr
    password: str


class RegistrationForm(Model):
    email: EmailStr
    name: Optional[str]
    password: str
    re_password: str

