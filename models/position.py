from sqlalchemy.orm import relationship

from models import NamedModel


class Position(NamedModel):
    __tablename__ = "positions"

    employee = relationship("Employee", back_populates="position")
