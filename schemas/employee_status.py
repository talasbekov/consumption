from datetime import date
from typing import Optional
from schemas import Model


class EmployeeStatusBase(Model):
    employee_id: int
    status_id: int
    start_date: date
    end_date: Optional[date]
    note: Optional[str]

class EmployeeStatusCreate(EmployeeStatusBase):
    pass

class EmployeeStatusUpdate(EmployeeStatusBase):
    pass

class EmployeeStatusRead(EmployeeStatusBase):
    id: int
    # status: Optional[StatusRead]  # Связанный статус

    class Config:
        orm_mode = True
