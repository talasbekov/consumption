from sqlalchemy.orm import relationship
from models import NamedModel


class Company(NamedModel):
    __tablename__ = "companies"

    departments = relationship("Departament", back_populates="companies")
    managements = relationship("Management", back_populates="companies")

