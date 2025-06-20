from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

# Assuming your SecondmentStatusEnum is in models.secondment
# Adjust the import path if it's located elsewhere or you prefer to redefine/copy it
from models.secondment import SecondmentStatusEnum

# Forward references for nested schemas if not defined yet or to avoid circular imports
# For example, if EmployeeRead and DivisionRead are defined in other schema files:
# from .employee import EmployeeRead # Assuming schemas.employee.EmployeeRead
# from .division import DivisionRead # Assuming schemas.division.DivisionRead
# For now, we'll use placeholders or assume they will be available in the global scope
# or defined later in this file for simplicity if they are very basic.

# Placeholder for actual Read schemas to be imported
class EmployeeRead(BaseModel): # Replace with actual import
    id: int
    # Add other relevant employee fields
    class Config:
        orm_mode = True

class DivisionRead(BaseModel): # Replace with actual import
    id: int
    nameRU: Optional[str] # Example field
    # Add other relevant division fields
    class Config:
        orm_mode = True

class UserRead(BaseModel): # Replace with actual import
    id: int
    email: Optional[str] # Example field
    class Config:
        orm_mode = True


class SecondmentLogBase(BaseModel):
    employee_id: int
    # original_division_id is often derived, not directly set by user during creation
    target_division_id: int
    secondment_start_date: date
    expected_end_date: Optional[date] = None
    # actual_end_date is usually set on update/completion
    # status is often managed internally, not directly set by user on creation
    initiating_user_id: Optional[int] = None
    approving_user_id: Optional[int] = None


class SecondmentLogCreate(SecondmentLogBase):
    # Potentially add original_division_id if it's not derived automatically by the service
    original_division_id: int # Explicitly require for creation if not derived
    pass


class SecondmentLogUpdate(BaseModel):
    target_division_id: Optional[int] = None
    secondment_start_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    status: Optional[SecondmentStatusEnum] = None
    approving_user_id: Optional[int] = None


class SecondmentLogRead(SecondmentLogBase):
    id: int
    original_division_id: int # Included for reading
    status: SecondmentStatusEnum
    actual_end_date: Optional[date] = None # Ensure this is part of the read model
    created_at: datetime
    updated_at: datetime

    # Nested representations for related objects
    employee: Optional[EmployeeRead] = None
    original_division: Optional[DivisionRead] = None
    target_division: Optional[DivisionRead] = None # target_division_id is already in Base
    initiating_user: Optional[UserRead] = None
    approving_user: Optional[UserRead] = None

    class Config:
        orm_mode = True
        use_enum_values = True # Ensures enum values are used in serialization if needed by client
        # If SecondmentStatusEnum is not str subclass, this might be important.
        # Since it is (str, enum.Enum), string values are default.
