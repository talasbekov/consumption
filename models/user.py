from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from models import NamedModel


class User(NamedModel):
    __tablename__ = "users"

    email = Column(String(150), nullable=True, unique=True)
    password = Column(String(255), nullable=True)
    last_signed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    login_count = Column(Integer, default=0)

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True, index=True)

    employees = relationship("Employee", back_populates="users")
