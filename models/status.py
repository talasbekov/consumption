from sqlalchemy.orm import relationship

from models import NamedModel


class Status(NamedModel):
    __tablename__ = "statuses"

    # Связь к таблице EmployeeStatus
    employee_statuses = relationship("EmployeeStatus", back_populates="status")
