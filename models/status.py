from sqlalchemy import Column, Date, Text
from sqlalchemy.orm import relationship

from models import NamedModel, status_employee_association


class Status(NamedModel):
    __tablename__ = "statuses"

    note = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    employees = relationship("Employee", secondary=status_employee_association, back_populates="statuses")
