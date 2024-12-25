from typing import List

from schemas import NamedModel, ManagementRead, DepartmentRead


class CompanyBase(NamedModel):

    class Config:
        orm_mode = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    departments: List[DepartmentRead]
    managements: List[ManagementRead]


