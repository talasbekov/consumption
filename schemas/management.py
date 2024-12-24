from typing import Optional, List
from pydantic import Field

from schemas import NamedModel, Model, DivisionRead


class ManagementBase(NamedModel):
    titleRU: Optional[str]
    titleKZ: Optional[str]
    titleEN: Optional[str]
    department_id: Optional[int]

    class Config:
        orm_mode = True


class ManagementCreate(ManagementBase):
    pass


class ManagementUpdate(ManagementBase):
    pass


class ManagementRead(Model):
    id: Optional[int]
    nameRU: Optional[str]
    divisions: List[DivisionRead] = Field(default_factory=list)

    class Config:
        orm_mode = True


class ManagementStateRead(Model):
    id: int
    nameRU: Optional[str]

    class Config:
        orm_mode = True
