from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from models import NamedModel
from models.base import TitledModel


class DivisionTypeEnum(str, enum.Enum):
    COMPANY = "Company"
    DEPARTMENT = "Департамент"
    DIRECTORATE = "Управление"
    DIVISION = "Отдел"


class Division(NamedModel, TitledModel):
    __tablename__ = "divisions"

    parent_division_id = Column(Integer, ForeignKey("divisions.id"), nullable=True)
    division_type = Column(Enum(DivisionTypeEnum), nullable=True)

    employees = relationship("Employee", back_populates="division")
