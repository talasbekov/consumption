# import os
from typing import Optional
from sqlalchemy.orm import Session

from models import Division  # Предполагается, что у вас есть модель Division в models.py
from schemas import DivisionCreate, DivisionUpdate # Предполагается, что у вас есть схемы создания и обновления событий
from services.base import ServiceBase


class DivisionService(ServiceBase[Division, DivisionCreate, DivisionUpdate]):

    def get_by_name(self, db: Session, name: str) -> Optional[Division]:
        return db.query(Division).filter(Division.name == name).first()

    # Количество сотрудников по штату всего департамента
    def get_count_emp_by_state(self):
        return 136


division_service = DivisionService(Division)
