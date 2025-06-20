from sqlalchemy.orm import relationship
from sqlalchemy import Column, SmallInteger

from models import NamedModel


class Position(NamedModel):
    __tablename__ = "positions"

    level = Column(SmallInteger, nullable=True)
    employee = relationship("Employee", back_populates="position")
