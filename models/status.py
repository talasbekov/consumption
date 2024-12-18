from sqlalchemy import Column, Date
from sqlalchemy.orm import relationship

from models import NamedModel


class Status(NamedModel):
    __tablename__ = "statuses"

    # note = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    employees = relationship("Employee", back_populates="statuses")
