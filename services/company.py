# import os
from typing import Optional
from sqlalchemy.orm import Session

from models import Company  # Предполагается, что у вас есть модель Company в models.py
from schemas import CompanyCreate, CompanyUpdate # Предполагается, что у вас есть схемы создания и обновления событий
from services.base import ServiceBase


class CompanyService(ServiceBase[Company, CompanyCreate, CompanyUpdate]):

    def get_by_name(self, db: Session, name: str) -> Optional[Company]:
        return db.query(Company).filter(Company.name == name).first()


company_service = CompanyService(Company)
