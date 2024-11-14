from typing import Optional

from schemas import NamedModel, Model


class PositionBase(NamedModel):
    category: Optional[str]


class PositionCreate(PositionBase):
    pass


class PositionUpdate(PositionBase):
    pass


class PositionRead(PositionBase, NamedModel):
    id: int


class PositionStateRead(Model):
    id: int
    name: Optional[str]

    class Config:
        orm_mode = True
