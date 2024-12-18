from typing import Optional, Text

from pydantic import root_validator

from schemas import Model, DivisionRead, RankRead, StatusRead


class EmployeeBase(Model):
    surname: Optional[str]
    firstname: Optional[str]
    patronymic: Optional[str]
    sort: Optional[int]
    status_id: Optional[int]
    rank_id: Optional[int]
    photo: Optional[str]
    division_id: Optional[int]
    note: Optional[Text]

    class Config:
        orm_mode = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeRead(EmployeeBase, Model):
    id: int
    divisions: Optional[DivisionRead]

    class Config:
        orm_mode = True


class EmployeeStateRead(Model):
    id: int
    surname: Optional[str]
    firstname: Optional[str]
    patronymic: Optional[str]
    sort: Optional[int]
    note: Optional[Text]
    photo: Optional[str]
    statuses: Optional[StatusRead]
    ranks: Optional[RankRead]
    # states: Optional[List[StateRead]]

    class Config:
        orm_mode = True

    @root_validator(pre=True)
    def clear_start_end_dates_if_active(cls, values):
        statuses = values.get("statuses")
        if statuses and statuses.name == "в строю":
            statuses.start_date = None
            statuses.end_date = None
        return values


class EmployeeRandomCreate(Model):
    surname: Optional[str]
    firstname: Optional[str]
    patronymic: Optional[str]
    sort: Optional[int]
    rank_id: Optional[int]
    position_id: Optional[int]
    status_id: Optional[int]
    division_id: Optional[int]


class EmployeeDataBulkUpdate(Model):
    employee_id: Optional[int]
    rank_id: Optional[int]
    sort: Optional[int]
    status_id: Optional[int]
    note: Optional[Text]

    class Config:
        orm_mode = True


class EmployeePhotoBulkUpdate(Model):
    employee_id: Optional[int]
    photo: Optional[str]
