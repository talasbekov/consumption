from sqlalchemy import Column, Date
from sqlalchemy.orm import relationship

from models import NamedModel


class Status(NamedModel):
    __tablename__ = "statuses"

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    employers = relationship("Employer", back_populates="statuses")
