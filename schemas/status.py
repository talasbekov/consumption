from datetime import date
from typing import Optional

from schemas import NamedModel


class StatusBase(NamedModel):
    start_date: Optional[date]
    end_date: Optional[date]


class StatusCreate(StatusBase):
    pass


class StatusUpdate(StatusBase):
    pass


class StatusRead(StatusBase, NamedModel):
    id: int

    class Config:
        orm_mode = True
