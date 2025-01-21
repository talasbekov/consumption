from sqlalchemy.orm import relationship
from models import NamedModel


class Company(NamedModel):
    __tablename__ = "companies"

    departments = relationship("Department", back_populates="company")
    managements = relationship("Management", back_populates="company")

