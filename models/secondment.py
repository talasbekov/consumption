import enum
from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from models.base import Model # Assuming Model is your base model from models.base
# It's important to know what 'Model' provides, e.g., id, created_at, updated_at.
# If Model already provides id, created_at, updated_at, they can be removed from SecondmentLog explicit definition.

class SecondmentStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RETURN_REQUESTED = "RETURN_REQUESTED"
    RETURN_APPROVED = "RETURN_APPROVED"
    ENDED = "ENDED"

class SecondmentLog(Model):
    __tablename__ = "secondment_logs"

    # If 'Model' doesn't provide id, uncomment the line below
    # id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    original_division_id = Column(Integer, ForeignKey("divisions.id"), nullable=False)
    target_division_id = Column(Integer, ForeignKey("divisions.id"), nullable=False)

    secondment_start_date = Column(Date, nullable=False)
    expected_end_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)

    status = Column(SQLAlchemyEnum(SecondmentStatusEnum), nullable=False, default=SecondmentStatusEnum.ACTIVE)

    initiating_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approving_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # If 'Model' doesn't provide created_at and updated_at, uncomment these lines
    # created_at = Column(DateTime, default=func.now())
    # updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    original_division = relationship("Division", foreign_keys=[original_division_id])
    target_division = relationship("Division", foreign_keys=[target_division_id])
    initiating_user = relationship("User", foreign_keys=[initiating_user_id])
    approving_user = relationship("User", foreign_keys=[approving_user_id])

    def __repr__(self):
        return f"<SecondmentLog(employee_id='{self.employee_id}', target_division_id='{self.target_division_id}', status='{self.status}')>"
