from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models import NamedModel


class Management(NamedModel):
    __tablename__ = "managements"

    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)

    company = relationship("Company", back_populates="managements")
    department = relationship("Department", back_populates="managements")
    divisions = relationship("Division", back_populates="management")
    employees = relationship("Employee", back_populates="management")
    states = relationship("State", back_populates="managements")
