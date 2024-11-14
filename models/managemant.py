from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models import NamedModel


class Management(NamedModel):
    __tablename__ = "managements"

    department_id = Column(Integer, ForeignKey("departments.id"))

    divisions = relationship("Division", back_populates="managements")
    departments = relationship("Department", back_populates="managements")
    states = relationship("State", back_populates="managements")
