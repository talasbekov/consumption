from typing import Optional, List

from schemas import NamedModel
from schemas.employee_status import EmployeeStatusRead


class StatusBase(NamedModel):
    pass

class StatusCreate(StatusBase):
    pass

class StatusUpdate(StatusBase):
    id: int

class StatusRead(StatusBase):
    id: int
    employee_statuses: Optional[List[EmployeeStatusRead]]  # Связи с сотрудниками

    class Config:
        orm_mode = True
