from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models import Model


class State(Model):
    __tablename__ = "states"

    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    management_id = Column(Integer, ForeignKey("managements.id", ondelete="SET NULL"), nullable=True)
    division_id = Column(Integer, ForeignKey("divisions.id", ondelete="SET NULL"), nullable=True)
    position_id = Column(Integer, ForeignKey("positions.id"))
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, unique=True)

    department = relationship("Department", back_populates="states", lazy="select")
    managements = relationship("Management", back_populates="states", lazy="select")
    divisions = relationship("Division", back_populates="states", lazy="select")
    positions = relationship("Position", back_populates="states", lazy="select")
    employees = relationship("Employee", back_populates="states")  # Используем lazy="joined", если вам нужны данные всегда

