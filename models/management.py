from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models import NamedModel


class Management(NamedModel):
    __tablename__ = "managements"

    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)

    companies = relationship("Company", back_populates="managements")
    departments = relationship("Department", back_populates="managements")
    divisions = relationship("Division", back_populates="managements")
    employees = relationship("Employee", back_populates="managements")
    states = relationship("State", back_populates="managements")
