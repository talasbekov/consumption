from sqlalchemy import Table, Column, Integer, ForeignKey
from core import Base

# Промежуточная таблица для связи многие ко многим между Operator и Event
status_employee_association = Table(
    "status_employees",
    Base.metadata,
    Column("status_id", Integer, ForeignKey("statuses.id"), primary_key=True),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)
