from typing import Optional, Text, List

from schemas import Model, DivisionRead, RankRead
from schemas.employee_status import EmployeeStatusUpdate, EmployeeStatusRead


class EmployeeBase(Model):
    surname: Optional[str]
    firstname: Optional[str]
    patronymic: Optional[str]
    iin: Optional[str]
    sort: Optional[int]
    rank_id: Optional[int]
    photo: Optional[str]
    management_id: Optional[int]
    division_id: Optional[int]
    note: Optional[Text]


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeRead(EmployeeBase, Model):
    id: int
    divisions: Optional[DivisionRead]
    statuses: Optional[List["EmployeeStatusRead"]]  # Связанные статусы сотрудника

    class Config:
        orm_mode = True


class EmployeeStateRead(Model):
    id: int
    surname: Optional[str]
    firstname: Optional[str]
    patronymic: Optional[str]
    iin: Optional[str]
    sort: Optional[int]
    note: Optional[Text]
    photo: Optional[str]
    statuses: Optional[List[EmployeeStatusRead]]  # Связанные статусы сотрудника
    ranks: Optional[RankRead]

    class Config:
        orm_mode = True

class EmployeeRandomCreate(Model):
    surname: Optional[str]
    firstname: Optional[str]
    patronymic: Optional[str]
    iin: Optional[int]
    sort: Optional[int]
    rank_id: Optional[int]
    position_id: Optional[int]
    division_id: Optional[int]


class EmployeeDataBulkUpdate(Model):
    employee_id: Optional[int]
    rank_id: Optional[int]
    sort: Optional[int]
    note: Optional[str]
    statuses: Optional[EmployeeStatusUpdate]# Список объектов статусов


class EmployeePhotoBulkUpdate(Model):
    employee_id: Optional[int]
    photo: Optional[str]
