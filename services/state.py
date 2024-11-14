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

from models import State, Employer, Status
from schemas import (
    StateCreate,
    StateUpdate,
)  # Предполагается, что у вас есть схемы создания и обновления событий
from schemas import EmployerDataBulkUpdate
from services import user_service

from services.base import ServiceBase


class StateService(ServiceBase[State, StateCreate, StateUpdate]):

    def get_by_employer_id(self, db: Session, employer_id: int) -> Optional[State]:
        return db.query(State).filter(State.employer_id == employer_id).first()

    async def update_employers_by_state(self, db: Session, employers_data: List[EmployerDataBulkUpdate]):
        try:
            # Парсим данные в объекты EmployerBulkUpdate
            employers_list = parse_obj_as(List[EmployerDataBulkUpdate], employers_data)

            for employer_data in employers_list:
                # Получаем запись работодателя по ID
                employer = db.query(Employer).filter(Employer.id == employer_data.id).first()
                if not employer:
                    logging.error(f"Employer with ID {employer_data.id} not found")
                    continue

                # Обновляем поля только если они заданы
                if employer_data.sort is not None:
                    employer.sort = employer_data.sort
                if employer_data.rank_id is not None:
                    employer.rank_id = employer_data.rank_id
                if employer_data.status_id is not None:
                    employer.status_id = employer_data.status_id

                # Добавляем работодателя в сессию
                db.add(employer)

            # Коммитим все изменения за один раз
            db.commit()
            logging.info("All employers updated successfully")

        except Exception as e:
            logging.error(f"Error while processing employers: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail="An error occurred while updating employers")


    def get_count_of_state(self, db: Session, user_id: int)-> dict[Any, int]:
        print(user_id)
        user = user_service.get_by_id(db, user_id)
        print(user.employer_id)
        emps = []
        states = db.query(self.model).all()
        for state in states:
            emps.append(state.employer_id)

        # Инициализируем state как None и создаем итератор по emps
        state = None
        index = 0

        # Используем цикл while для перебора emps
        while state is None and index < len(emps):
            employer_id = emps[index]
            state = db.query(self.model).filter(self.model.employer_id == employer_id).first()
            index += 1

        # Теперь state содержит либо значение, либо остался None, если подходящего значения не нашлось
        if state is not None:
            print("Found state:", state)
        else:
            print("No valid state found")

        state_count = db.query(self.model).filter(self.model.department_id == state.department_id).count()
        vacant_count = db.query(self.model).filter(self.model.employer_id.is_(None)).count()
        print(state_count, vacant_count)
        by_list_count = state_count - vacant_count
        inline_count = (
            db.query(Employer)
            .join(State)
            .join(Status)
            .filter(state.department_id == State.department_id)
            .filter(Status.name == "в строю")
            .count()
        )
        by_status_count = by_list_count - inline_count
        on_sick_leave_count = (
            db.query(Employer)
            .join(State)
            .join(Status)
            .filter(state.department_id == State.department_id)
            .filter(Status.name == "на больничном")
            .count()
        )
        on_leave = (
            db.query(Employer)
            .join(State)
            .join(Status)
            .filter(state.department_id == State.department_id)
            .filter(Status.name == "в отпуске")
            .count()
        )
        business_trip_count = (
            db.query(Employer)
            .join(State)
            .join(Status)
            .filter(state.department_id == State.department_id)
            .filter(Status.name == "в командировке")
            .count()
        )
        on_duty_count = (
            db.query(Employer)
            .join(State)
            .join(Status)
            .filter(state.department_id == State.department_id)
            .filter(Status.name == "на дежурстве")
            .count()
        )
        after_duty = (
            db.query(Employer)
            .join(State)
            .join(Status)
            .filter(state.department_id == State.department_id)
            .filter(Status.name == "после дежурства")
            .count()
        )
        on_studying_count = (
            db.query(Employer)
            .join(State)
            .join(Status)
            .filter(state.department_id == State.department_id)
            .filter(Status.name == "на соревновании")
            .count()
        )
        on_seconded = (
            db.query(Employer)
            .join(State)
            .join(Status)
            .filter(state.department_id == State.department_id)
            .filter(Status.name == "прикомандирован")
            .count()
        )
        out_seconded = (
            db.query(Employer)
            .join(State)
            .join(Status)
            .filter(state.department_id == State.department_id)
            .filter(Status.name == "откомандирован")
            .count()
        )

        return {
            "state_count": state_count,
            "vacant_count": vacant_count,
            "by_list_count": by_list_count,
            "inline_count": inline_count,
            "by_status_count": by_status_count,
            "on_sick_leave_count": on_sick_leave_count,
            "on_leave": on_leave,
            "business_trip_count": business_trip_count,
            "on_duty_count": on_duty_count,
            "after_duty": after_duty,
            "on_studying_count": on_studying_count,
            "on_seconded": on_seconded,
            "out_seconded": out_seconded
        }

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
