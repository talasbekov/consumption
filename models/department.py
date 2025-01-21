from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from models import NamedModel


class Department(NamedModel):
    __tablename__ = "departments"

    titleRU = Column("titleru", Text, nullable=True)
    titleKZ = Column("titlekz", Text, nullable=True)
    titleEN = Column("titleen", Text, nullable=True)

    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))

    company = relationship("Company", back_populates="departments")
    managements = relationship("Management", back_populates="department")
    divisions = relationship("Division", back_populates="department")
    states = relationship("State", back_populates="department")
