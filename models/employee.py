from sqlalchemy import Column, String, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from models import Model


class Employee(Model):
    __tablename__ = "employees"

    surname = Column(String(128))
    firstname = Column(String(128))
    patronymic = Column(String(128))
    iin = Column(String, nullable=True, index=True)
    sort = Column(Integer, nullable=False)
    photo = Column(String, nullable=True)
    note = Column(Text, nullable=True)

    rank_id = Column(Integer, ForeignKey("ranks.id"))
    division_id = Column(Integer, ForeignKey("divisions.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)

    ranks = relationship("Rank", back_populates="employees")
    divisions = relationship("Division", back_populates="employees")
    position = relationship("Position", back_populates="employee")
    # Связь с промежуточной таблицей EmployeeStatus
    statuses = relationship("EmployeeStatus", back_populates="employee")
    users = relationship("User", back_populates="employees")

