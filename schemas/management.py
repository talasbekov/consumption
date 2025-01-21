from typing import Optional, List

from schemas import NamedModel, Model, DivisionRead


class ManagementBase(NamedModel):
    titleRU: Optional[str]
    titleKZ: Optional[str]
    titleEN: Optional[str]
    company_id: Optional[int]
    department_id: Optional[int]


class ManagementCreate(ManagementBase):
    pass


class ManagementUpdate(ManagementBase):
    pass


class ManagementRead(Model):
    id: Optional[int]
    nameRU: Optional[str]
    divisions: Optional[List[DivisionRead]]

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        # Если divisions пустой список, заменяем на None
        if isinstance(data['divisions'], list) and not data['divisions']:
            data['divisions'] = None
        return data


class ManagementStateRead(Model):
    id: int
    nameRU: Optional[str]
    titleRU: Optional[str]
