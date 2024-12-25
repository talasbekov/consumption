from typing import Optional, List

from schemas import NamedModel, Model, ManagementRead


class DepartmentBase(NamedModel):
    titleRU: Optional[str]
    titleKZ: Optional[str]
    titleEN: Optional[str]
    company_id: Optional[int]


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    pass


class DepartmentRead(Model):
    id: int
    nameRU: Optional[str]
    managements: List[ManagementRead]


class DepartmentStateRead(Model):
    id: int
    nameRU: Optional[str]
