from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from models import NamedModel


class Rank(NamedModel):
    __tablename__ = "ranks"

    employees = relationship("Employee", back_populates="ranks")
