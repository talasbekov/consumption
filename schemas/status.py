from datetime import date
from typing import Optional

from schemas import NamedModel, Model


class StatusBase(NamedModel):
    start_date: Optional[date]
    end_date: Optional[date]


class StatusCreate(StatusBase):
    pass


class StatusUpdate(Model):
    id: int
    note: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]


class StatusRead(StatusBase, NamedModel):
    id: int
