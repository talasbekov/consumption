from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models import NamedModel
from models.base import TitledModel


class Division(NamedModel, TitledModel):
    __tablename__ = "divisions"

    parent_division_id = Column(Integer, ForeignKey("divisions.id"), nullable=True)

    employees = relationship("Employee", back_populates="division")
