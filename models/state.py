from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models import Model


class State(Model):
    __tablename__ = "states"

    department_id = Column(Integer, ForeignKey("departments.id"))
    management_id = Column(Integer, ForeignKey("managements.id"))
    division_id = Column(Integer, ForeignKey("divisions.id"))
    position_id = Column(Integer, ForeignKey("positions.id"))
    employer_id = Column(Integer, ForeignKey("employers.id"), nullable=True, unique=True)

    departments = relationship("Department", back_populates="states", lazy="select")
    managements = relationship("Management", back_populates="states", lazy="select")
    divisions = relationship("Division", back_populates="states", lazy="select")
    positions = relationship("Position", back_populates="states", lazy="select")
    employers = relationship("Employer", back_populates="states")  # Используем lazy="joined", если вам нужны данные всегда

