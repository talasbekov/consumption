from sqlalchemy.orm import relationship
from sqlalchemy import Column, String # Added String

from models import NamedModel


class Status(NamedModel):
    __tablename__ = "statuses"

    code = Column(String(50), unique=True, nullable=True, index=True) # Added code column

    # Связь к таблице EmployeeStatus
    employee_statuses = relationship("EmployeeStatus", back_populates="status")
