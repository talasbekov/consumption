from datetime import date
from typing import Optional
from schemas import Model, StatusRead


class EmployeeStatusBase(Model):
    employee_id: int
    status_id: int
    start_date: Optional[date]
    end_date: Optional[date]
    note: Optional[str]

class EmployeeStatusCreate(EmployeeStatusBase):
    pass

class EmployeeStatusUpdate(EmployeeStatusBase):
    pass

class EmployeeStatusRead(EmployeeStatusBase):
    id: Optional[int]
    status: Optional[StatusRead]  # Связанный статус

    class Config:
        orm_mode = True
