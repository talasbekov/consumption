from typing import Optional
from sqlalchemy.orm import Session

from models import Position  # Предполагается, что у вас есть модель Position в models.py
from schemas import (
    PositionCreate,
    PositionUpdate,
)  # Предполагается, что у вас есть схемы создания и обновления событий

from services.base import ServiceBase


class PositionService(ServiceBase[Position, PositionCreate, PositionUpdate]):

    def get_by_name(self, db: Session, name: str) -> Optional[Position]:
        return db.query(Position).filter(Position.name == name).first()


position_service = PositionService(Position)
