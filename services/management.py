from typing import Optional
from sqlalchemy.orm import Session

from models import Management  # Предполагается, что у вас есть модель Management в models.py
from schemas import (
    ManagementCreate,
    ManagementUpdate,
)  # Предполагается, что у вас есть схемы создания и обновления событий

from services.base import ServiceBase


class ManagementService(ServiceBase[Management, ManagementCreate, ManagementUpdate]):

    def get_by_name(self, db: Session, name: str) -> Optional[Management]:
        return db.query(Management).filter(Management.name == name).first()


management_service = ManagementService(Management)
