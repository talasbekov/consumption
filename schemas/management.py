from typing import Optional, List

from schemas import NamedModel, Model, DivisionRead


class ManagementBase(NamedModel):
    titleRU: Optional[str]
    titleKZ: Optional[str]
    titleEN: Optional[str]
    department_id: Optional[int]


class ManagementCreate(ManagementBase):
    pass


class ManagementUpdate(ManagementBase):
    pass


class ManagementRead(Model):
    id: Optional[int]
    nameRU: Optional[str]
    divisions: List[DivisionRead]


class ManagementStateRead(Model):
    id: int
    nameRU: Optional[str]
