from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from models import Model


class User(Model):
    __tablename__ = "users"

    email = Column(String(150), nullable=True, unique=True)
    password = Column(String(255), nullable=True)
    last_signed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    login_count = Column(Integer, default=0)
    role = Column(Integer, nullable=True)  # Added role column

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True, index=True)

    employees = relationship("Employee", back_populates="users")
