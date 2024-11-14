from typing import Optional

from schemas import Model, DepartmentStateRead, ManagementStateRead, DivisionStateRead, PositionStateRead, EmployerStateRead

class StateBase(Model):
    department_id: Optional[int]
    management_id: Optional[int]
    division_id: Optional[int]
    position_id: Optional[int]
    employer_id: Optional[int]

    class Config:
        orm_mode = True


class StateCreate(StateBase):
    pass


class StateUpdate(StateBase):
    pass


class StateRead(Model):
    id: Optional[int]
    departments: Optional[DepartmentStateRead]
    managements: Optional[ManagementStateRead]
    divisions: Optional[DivisionStateRead]
    positions: Optional[PositionStateRead]
    employers: Optional[EmployerStateRead]

    class Config:
        orm_mode = True


class StateEmployerRead(Model):
    id: int
    positions: Optional[PositionStateRead]
    employers: Optional[EmployerStateRead]

    class Config:
        orm_mode = True


class StateRandomCreate(Model):
    department_id: Optional[int]
    management_id: Optional[int]
    division_id: Optional[int]
    position_id: Optional[int]
    employer_id: Optional[int]


class StateTreeRead(Model):
    id: int
    departments: Optional[DepartmentStateRead]
    managements: Optional[ManagementStateRead]
    divisions: Optional[DivisionStateRead]

    class Config:
        orm_mode = True