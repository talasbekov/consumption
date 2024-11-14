from typing import Optional
from sqlalchemy.orm import Session, joinedload

from models import Department, Management  # Предполагается, что у вас есть модель Department в models.py
from schemas import DepartmentCreate, DepartmentUpdate # Предполагается, что у вас есть схемы создания и обновления событий

from services.base import ServiceBase


class DepartmentService(ServiceBase[Department, DepartmentCreate, DepartmentUpdate]):

    def get_by_name(self, db: Session, name: str) -> Optional[Department]:
        return db.query(Department).filter(Department.name == name).first()

    def department_to_dict(self, department: Department):
        return {
            "id": department.id,
            "name": department.name,
            "managements": [
                {
                    "id": management.id,
                    "name": management.name,
                    "divisions": [
                        {
                            "id": division.id,
                            "name": division.name
                        } for division in management.divisions
                    ]
                } for management in department.managements
            ]
        }

    def get_all_tree(self, db: Session) -> list[dict]:
        results = db.query(Department).options(
            joinedload(Department.managements).joinedload(Management.divisions)
        ).all()
        tree_data = [self.department_to_dict(department) for department in results]
        print(tree_data)
        return tree_data


department_service = DepartmentService(Department)
