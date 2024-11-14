import datetime
from typing import Optional

from pydantic import BaseModel


class Model(BaseModel):

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class NamesModel(Model):
    id: int
    name: Optional[str]

    class Config:
        orm_mode = True


class NamedModel(Model):
    name: Optional[str]
    nameKZ: Optional[str]
    nameEN: Optional[str]

    class Config:
        orm_mode = True


class TextModel(Model):
    text: str
    textKZ: Optional[str]
    textEN: Optional[str]

    class Config:
        orm_mode = True


class ReadModel(Model):
    id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class ReadNamedModel(NamedModel, ReadModel):
    name: Optional[str]
    nameKZ: Optional[str]
    nameEN: Optional[str]


class ReadTextModel(TextModel, ReadModel):
    text: Optional[str]
    textKZ: Optional[str]
    textEN: Optional[str]
