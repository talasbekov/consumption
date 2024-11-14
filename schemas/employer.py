from typing import Optional, Text

from schemas import Model, DivisionRead, RankRead, StatusRead


class EmployerBase(Model):
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


class EmployerCreate(EmployerBase):
    pass


class EmployerUpdate(EmployerBase):
    pass


class EmployerRead(EmployerBase, Model):
    id: int
    divisions: Optional[DivisionRead]

    class Config:
        orm_mode = True

class EmployerStateRead(Model):
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


class EmployerRandomCreate(Model):
    surname: Optional[str]
    firstname: Optional[str]
    patronymic: Optional[str]
    sort: Optional[int]
    rank_id: Optional[int]
    position_id: Optional[int]
    status_id: Optional[int]
    division_id: Optional[int]


class EmployerDataBulkUpdate(Model):
    employer_id: Optional[int]
    rank_id: Optional[int]
    sort: Optional[int]
    status_id: Optional[int]
    note: Optional[Text]

    class Config:
        orm_mode = True


class EmployerPhotoBulkUpdate(Model):
    employer_id: Optional[int]
    photo: Optional[str]
