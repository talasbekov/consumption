from typing import Optional, List

from schemas import NamedModel, Model, ManagementRead, DepartmentRead


class CompanyBase(NamedModel):

    class Config:
        orm_mode = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class CompanyRead(Model):
    id: int
    name: Optional[str]
    departments: List[DepartmentRead]
    managements: List[ManagementRead]


