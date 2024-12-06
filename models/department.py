from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models import NamedModel


class Department(NamedModel):
    __tablename__ = "departments"

    companies_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))

    companies = relationship("Company", back_populates="departments")
    managements = relationship("Management", back_populates="departments")
    divisions = relationship("Division", back_populates="managements")
    states = relationship("State", back_populates="departments")
