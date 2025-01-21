from typing import Optional

from schemas import NamedModel, Model


class PositionBase(NamedModel):
    pass


class PositionCreate(PositionBase):
    pass


class PositionUpdate(PositionBase):
    pass


class PositionRead(PositionBase, NamedModel):
    id: int


class PositionStateRead(Model):
    id: int
    nameRU: Optional[str]
