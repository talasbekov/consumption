from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from models import Model


class Rank(Model):
    __tablename__ = "ranks"

    name = Column(String(250))

    employees = relationship("Employee", back_populates="ranks")
