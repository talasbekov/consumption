from typing import Optional
from sqlalchemy.orm import Session

from models import Status  # Предполагается, что у вас есть модель Status в models.py
from schemas import (
    StatusCreate,
    StatusUpdate,
)  # Предполагается, что у вас есть схемы создания и обновления событий

from services.base import ServiceBase


class StatusService(ServiceBase[Status, StatusCreate, StatusUpdate]):

    def get_by_name(self, db: Session, name: str) -> Optional[Status]:
        return db.query(Status).filter(Status.name == name).first()


status_service = StatusService(Status)
