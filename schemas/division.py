from typing import Optional
from schemas import NamedModel, Model


class DivisionBase(NamedModel):
    titleRU: Optional[str]
    titleKZ: Optional[str]
    titleEN: Optional[str]
    department_id: Optional[int]
    management_id: Optional[int]


class DivisionCreate(DivisionBase):
    pass


class DivisionUpdate(DivisionBase):
    pass


class DivisionRead(Model):
    id: Optional[int]
    name: Optional[str]


class DivisionStateRead(Model):
    id: int
    nameRU: Optional[str]
    titleRU: Optional[str]
