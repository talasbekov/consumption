from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models import NamedModel


class Division(NamedModel):
    __tablename__ = "divisions"

    management_id = Column(Integer, ForeignKey("managements.id"))

    employers = relationship("Employer", back_populates="divisions")
    managements = relationship("Management", back_populates="divisions")
    states = relationship("State", back_populates="divisions")
