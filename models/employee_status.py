from sqlalchemy import Column, Integer, ForeignKey, Date, Text
from sqlalchemy.orm import relationship

from models import Model


class EmployeeStatus(Model):
    __tablename__ = "employee_status"

    employee_id = Column(Integer, ForeignKey("employees.id"))
    status_id = Column(Integer, ForeignKey("statuses.id"))

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    note = Column(Text, nullable=True)

    # Обратные связи
    employee = relationship("Employee", back_populates="statuses")
    status = relationship("Status", back_populates="employee_statuses")
