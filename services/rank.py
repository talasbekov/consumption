from typing import Optional
from sqlalchemy.orm import Session

from models import Rank  # Предполагается, что у вас есть модель Rank в models.py
from schemas import (
    RankCreate,
    RankUpdate,
)  # Предполагается, что у вас есть схемы создания и обновления событий

from services.base import ServiceBase


class RankService(ServiceBase[Rank, RankCreate, RankUpdate]):

    def get_by_name(self, db: Session, name: str) -> Optional[Rank]:
        return db.query(Rank).filter(Rank.name == name).first()


rank_service = RankService(Rank)
