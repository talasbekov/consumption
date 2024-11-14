from typing import Optional
from schemas import NamedModel, Model


class DivisionBase(NamedModel):
    management_id: Optional[int]

    class Config:
        orm_mode = True


class DivisionCreate(DivisionBase):
    pass


class DivisionUpdate(DivisionBase):
    pass


class DivisionRead(Model):
    id: Optional[int]
    name: Optional[str]


class DivisionStateRead(Model):
    id: int
    name: Optional[str]

    class Config:
        orm_mode = True
