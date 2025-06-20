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

# Schemas for bulk status updates
from pydantic import BaseModel
from typing import List

class BulkStatusUpdateItemSchema(BaseModel):
    employee_id: int
    status: str  # e.g., "ON_DUTY" (corresponds to Status.code)

class BulkStatusUpdateRequestSchema(BaseModel):
    date_from: date
    date_to: Optional[date] = None
    comment: Optional[str] = None
    items: List[BulkStatusUpdateItemSchema]

class BulkStatusUpdateResponseSchema(BaseModel):
    updated: int = 0
    skipped: int = 0
    errors: List[str] = []
