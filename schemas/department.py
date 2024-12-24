from typing import Optional, List

from pydantic import Field

from schemas import NamedModel, Model, ManagementRead


class DepartmentBase(NamedModel):
    titleRU: Optional[str]
    titleKZ: Optional[str]
    titleEN: Optional[str]

    class Config:
        orm_mode = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    pass


class DepartmentRead(Model):
    id: int
    nameRU: Optional[str]
    managements: List[ManagementRead] = Field(default_factory=list)


class DepartmentStateRead(Model):
    id: int
    nameRU: Optional[str]

    class Config:
        orm_mode = True

