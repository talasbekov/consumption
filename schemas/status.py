from schemas import NamedModel


class StatusBase(NamedModel):
    pass

class StatusCreate(StatusBase):
    pass

class StatusUpdate(StatusBase):
    id: int

class StatusRead(StatusBase):
    id: int  # Связи с сотрудниками

    class Config:
        orm_mode = True
