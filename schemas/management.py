from typing import Optional, List

from schemas import NamedModel, Model, DivisionRead


class ManagementBase(NamedModel):
    department_id: Optional[int]

    class Config:
        orm_mode = True


class ManagementCreate(ManagementBase):
    pass


class ManagementUpdate(ManagementBase):
    pass


class ManagementRead(Model):
    id: Optional[int]
    name: Optional[str]
    divisions: List[DivisionRead] = []

    class Config:
        orm_mode = True


class ManagementStateRead(Model):
    id: int
    name: Optional[str]

    class Config:
        orm_mode = True
