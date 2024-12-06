import logging
import os
from typing import Optional, Any, List
from fastapi import HTTPException
from pydantic.tools import parse_obj_as
from sqlalchemy.orm import Session

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from io import BytesIO

from models import State, Employee, Status
from schemas import (
    StateCreate,
    StateUpdate,
)  # Предполагается, что у вас есть схемы создания и обновления событий
from schemas import EmployeeDataBulkUpdate
from services import user_service

from services.base import ServiceBase


class StateService(ServiceBase[State, StateCreate, StateUpdate]):

    def get_by_employee_id(self, db: Session, employee_id: int) -> Optional[State]:
        return db.query(State).filter(State.employee_id == employee_id).first()

    async def update_employees_by_state(self, db: Session, employees_data: List[EmployeeDataBulkUpdate]):
        try:
            # Парсим данные в объекты EmployeeBulkUpdate
            employees_list = parse_obj_as(List[EmployeeDataBulkUpdate], employees_data)

            for employee_data in employees_list:
                # Получаем запись работодателя по ID
                employee = db.query(Employee).filter(Employee.id == employee_data.id).first()
                if not employee:
                    logging.error(f"Employee with ID {employee_data.id} not found")
                    continue

                # Обновляем поля только если они заданы
                if employee_data.sort is not None:
                    employee.sort = employee_data.sort
                if employee_data.rank_id is not None:
                    employee.rank_id = employee_data.rank_id
                if employee_data.status_id is not None:
                    employee.status_id = employee_data.status_id

                # Добавляем работодателя в сессию
                db.add(employee)

            # Коммитим все изменения за один раз
            db.commit()
            logging.info("All employees updated successfully")

        except Exception as e:
            logging.error(f"Error while processing employees: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail="An error occurred while updating employees")


    def get_count_of_state(self, db: Session, user_id: int)-> dict[Any, int]:
        print(user_id)
        user = user_service.get_by_id(db, user_id)
        print(user.employee_id)
        emps = []
        states = db.query(self.model).all()
        for state in states:
            emps.append(state.employee_id)

        # Инициализируем state как None и создаем итератор по emps
        state = None
        index = 0

        # Используем цикл while для перебора emps
        while state is None and index < len(emps):
            employee_id = emps[index]
            state = db.query(self.model).filter(self.model.employee_id == employee_id).first()
            index += 1

        # Теперь state содержит либо значение, либо остался None, если подходящего значения не нашлось
        if state is not None:
            print("Found state:", state)
        else:
            print("No valid state found")

        state_count = db.query(self.model).filter(self.model.department_id == state.department_id).count()
        vacant_count = db.query(self.model).filter(self.model.employee_id.is_(None)).count()
        by_list_count = state_count - vacant_count
        inline_count = (
            db.query(Employee)
            .join(State)
            .join(Status)
            .filter(state.department_id == State.department_id)
            .filter(Status.name == "в строю")
            .count()
        )
        by_status_count = by_list_count - inline_count

        # Формируем начальный словарь
        result = {
            "by state": {"count": state_count, "name": "по штату"},
            "by vacant": {"count": vacant_count, "name": "ваканты"},
            "by list": {"count": by_list_count, "name": "по списку"},
            "by status": {"count": by_status_count, "name": "общее количество отсутствующих"},
        }

        # Обрабатываем статусы
        statuses = db.query(Status).all()
        for status in statuses:
            count = (
                db.query(Employee)
                .join(State)
                .join(Status)
                .filter(state.department_id == State.department_id)
                .filter(Status.name == status.name)
                .count()
            )
            # Добавляем данные по каждому статусу в словарь
            result[status.nameEN] = {"count": count, "name": status.name}

        # Возвращаем итоговый словарь
        return result

    def create_word_report_from_template(self, db: Session, user_id: int):
        """
        Создание отчета Word с подстановкой данных из функции get_count_of_state.
        """
        # Получаем данные из функции get_count_of_state
        data = self.get_count_of_state(db, user_id)

        file_path = './template.docx'
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден. Пожалуйста, проверьте путь к файлу.")

        doc = Document(file_path)

        # Заполнение таблицы значениями из data
        for table in doc.tables:
            row_idx = 4  # Индекс строки, с которой начинается заполнение

            row = table.rows[row_idx]
            values = [
                str(data.get("state_count", 0)),
                str(data.get("by_list_count", 0)),
                str(data.get("inline_count", 0)),
                str(data.get("vacant_count", 0)),
                str(data.get("on_leave", 0)),
                str(data.get("business_trip_count", 0)),
                str(data.get("on_sick_leave_count", 0)),
                str(data.get("on_duty_count", 0)),
                str(data.get("after_duty", 0)),
                str(data.get("on_studying_count", 0)),
                str(data.get("on_seconded", 0)),
                str(data.get("out_seconded", 0))
            ]

            # Заполнение ячеек таблицы данными
            for cell_idx, value in enumerate(values, start=2):
                cell = row.cells[cell_idx]
                cell.text = value

                # Настройка выравнивания и стиля текста
                paragraph = cell.paragraphs[0]
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.runs[0]
                run.font.size = Pt(12)
                run.font.name = 'Times New Roman'

                # Вертикальное выравнивание
                tc = cell._element
                tcPr = tc.get_or_add_tcPr()
                tcVAlign = OxmlElement('w:vAlign')
                tcVAlign.set(qn('w:val'), 'bottom')
                tcPr.append(tcVAlign)

            row_idx += 1

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        return buffer


state_service = StateService(State)
