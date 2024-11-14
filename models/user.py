from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from models import NamedModel


class User(NamedModel):
    __tablename__ = "users"

    email = Column(String(150), nullable=True, unique=True)
    password = Column(String(255), nullable=True)
    workplace = Column(String(128))
    iin = Column(Integer, unique=True)
    phone_number = Column(String(20), nullable=True)
    is_accreditator = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    last_signed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    login_count = Column(Integer, default=0)

    employer_id = Column(Integer, ForeignKey("employers.id"))

    employers = relationship("Employer", back_populates="users")
