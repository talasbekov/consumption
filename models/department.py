from sqlalchemy.orm import relationship

from models import NamedModel


class Department(NamedModel):
    __tablename__ = "departments"

    managements = relationship("Management", back_populates="departments")
    states = relationship("State", back_populates="departments")
