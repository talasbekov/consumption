from sqlalchemy import Column, String, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from models import Model


class Employee(Model):
    __tablename__ = "employees"

    surname = Column(String(128))
    firstname = Column(String(128))
    patronymic = Column(String(128))
    sort = Column(Integer, nullable=False)
    photo = Column(String, nullable=True)
    note = Column(Text, nullable=True)

    rank_id = Column(Integer, ForeignKey("ranks.id"))
    division_id = Column(Integer, ForeignKey("divisions.id"), nullable=True)
    management_id = Column(Integer, ForeignKey("managements.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("statuses.id"))

    management = relationship("Management", back_populates="employees", lazy="select")
    division = relationship("Division", back_populates="employees", lazy="select")
    states = relationship("State", back_populates="employees", lazy="joined")  # Используем lazy="joined", чтобы всегда делать JOIN
    ranks = relationship("Rank", back_populates="employees", lazy="select")
    statuses = relationship("Status", back_populates="employees", lazy="select")
    users = relationship("User", back_populates="employees", lazy="select")

