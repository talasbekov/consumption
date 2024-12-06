from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models import NamedModel


class Division(NamedModel):
    __tablename__ = "divisions"

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    management_id = Column(Integer, ForeignKey("managements.id"), nullable=True)

    department = relationship("Department", back_populates="divisions")
    management = relationship("Management", back_populates="divisions")
    employees = relationship("Employee", back_populates="division")
    states = relationship("State", back_populates="divisions")
