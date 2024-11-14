from typing import Optional, List

from schemas import NamedModel, Model, ManagementRead


class DepartmentBase(NamedModel):

    class Config:
        orm_mode = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    pass


class DepartmentRead(Model):
    id: int
    name: Optional[str]
    managements: List[ManagementRead] = []


class DepartmentStateRead(Model):
    id: int
    name: Optional[str]

    class Config:
        orm_mode = True

