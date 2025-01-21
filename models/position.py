from sqlalchemy.orm import relationship

from models import NamedModel


class Position(NamedModel):
    __tablename__ = "positions"

    states = relationship("State", back_populates="positions")
