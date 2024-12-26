import logging
import os
from datetime import datetime
from typing import Optional, Any, List
from fastapi import HTTPException
from pydantic.tools import parse_obj_as
from collections import defaultdict
from sqlalchemy.orm import Session

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from io import BytesIO

from models import State, Employee, Status, Management, status_employee_association
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

    # async def update_employees_by_state(self, db: Session, employees_data: List[EmployeeDataBulkUpdate]):
    #     try:
    #         # Парсим данные в объекты EmployeeBulkUpdate
    #         employees_list = parse_obj_as(List[EmployeeDataBulkUpdate], employees_data)
    #
    #         for employee_data in employees_list:
    #             # Получаем запись работодателя по ID
    #             employee = db.query(Employee).filter(Employee.id == employee_data.id).first()
    #             if not employee:
    #                 logging.error(f"Employee with ID {employee_data.id} not found")
    #                 continue
    #
    #             # Обновляем поля только если они заданы
    #             if employee_data.sort is not None:
    #                 employee.sort = employee_data.sort
    #             if employee_data.rank_id is not None:
    #                 employee.rank_id = employee_data.rank_id
    #             if employee_data.status_id is not None:
    #                 employee.status_id = employee_data.status_id
    #
    #             # Добавляем работодателя в сессию
    #             db.add(employee)
    #
    #         # Коммитим все изменения за один раз
    #         db.commit()
    #         logging.info("All employees updated successfully")
    #
    #     except Exception as e:
    #         logging.error(f"Error while processing employees: {e}")
    #         db.rollback()
    #         raise HTTPException(status_code=500, detail="An error occurred while updating employees")

    async def update_employees_by_state(self, db: Session, employees_data: List[EmployeeDataBulkUpdate]):
        try:
            # Парсим данные в объекты EmployeeBulkUpdate
            employees_list = parse_obj_as(List[EmployeeDataBulkUpdate], employees_data)

            for employee_data in employees_list:
                # Получаем запись сотрудника по ID
                employee = db.query(Employee).filter(Employee.id == employee_data.employee_id).first()
                if not employee:
                    logging.error(f"Employee with ID {employee_data.employee_id} not found")
                    continue

                # Обновляем поля только если они заданы
                if employee_data.sort is not None:
                    employee.sort = employee_data.sort
                if employee_data.rank_id is not None:
                    employee.rank_id = employee_data.rank_id

                # Обновление статусов, если они переданы
                if employee_data.statuses:
                    # Очищаем старые статусы или добавляем новые
                    new_status = Status(
                        start_date=employee_data.statuses.start_date,
                        end_date=employee_data.statuses.end_date,
                        note=employee_data.statuses.note,
                    )
                    employee.statuses.append(new_status)

                logging.info(f"Employee with ID {employee_data.employee_id} updated successfully")

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
            .join(Employee.statuses)  # Присоединяем таблицу Status через отношение
            .join(State, State.employee_id == Employee.id)  # Присоединяем State по employee_id
            .filter(State.department_id == state.department_id)  # Фильтруем по department_id
            .filter(Status.nameRU == "в строю")  # Условие для статуса
            .count()
        )
        by_status_count = by_list_count - inline_count

        # Формируем начальный словарь
        result = {
            "by state": {"count": state_count, "name": "по штату"},
            "by list": {"count": by_list_count, "name": "по списку"},
            "by vacant": {"count": vacant_count, "name": "ваканты"},
            "by status": {"count": by_status_count, "name": "общее количество отсутствующих"},
        }

        # Обрабатываем статусы
        statuses = db.query(Status).all()
        for status in statuses:
            count = (
                db.query(Employee)
                .join(Employee.statuses)  # Присоединяем таблицу Status через отношение
                .join(State, State.employee_id == Employee.id)  # Присоединяем State по employee_id
                .filter(State.department_id == state.department_id)  # Фильтруем по department_id
                .filter(Status.nameRU == status.nameRU)  # Фильтруем по имени статуса
                .count()
            )

            # Добавляем данные по каждому статусу в словарь
            result[status.nameEN] = {"count": count, "name": status.nameRU}

        # Возвращаем итоговый словарь
        return result

    def get_count_of_management_state(self, db: Session, user_id: int) -> dict[str, dict[str, dict[str, int]]]:
        # Получаем пользователя по user_id
        user = user_service.get_by_id(db, user_id)
        state = self.get_by_employee_id(db, user.employee_id)

        if state is not None:
            print("Found state:", state)
        else:
            print("No valid state found")

        # Получаем общее количество из первой функции
        overall_count = self.get_count_of_state(db, user_id)

        # Инициализируем итоговый словарь
        result = {}

        # Получаем все управления для текущего отдела
        managements = db.query(Management).filter(Management.department_id == state.department_id).all()

        for management in managements:
            # Считаем количество по штату, вакантных сотрудников и т.д.
            state_count = db.query(self.model).filter(self.model.department_id == management.department_id,
                                                      self.model.management_id == management.id).count()
            vacant_count = db.query(self.model).filter(self.model.employee_id.is_(None),
                                                       self.model.department_id == management.department_id,
                                                       self.model.management_id == management.id).count()
            by_list_count = state_count - vacant_count
            # inline_count = (
            #     db.query(Employee)
            #     .join(State)
            #     .join(Status)
            #     .filter(State.department_id == management.department_id,
            #             State.management_id == management.id)
            #     .filter(Status.nameRU == "в строю")
            #     .count()
            # )
            # by_status_count = by_list_count - inline_count

            # Формируем структуру для управления
            management_data = {
                "by state": {"count": state_count, "name": "по штату"},
                "by list": {"count": by_list_count, "name": "по списку"},
                "by vacant": {"count": vacant_count, "name": "ваканты"},
                # "by status": {"count": by_status_count, "name": "общее количество отсутствующих"}
            }

            # Получаем данные по каждому статусу
            statuses = db.query(Status).all()
            for status in statuses:
                count = (
                    db.query(Employee)
                    .join(Employee.statuses)  # Присоединяем таблицу Status через отношение
                    .join(State, State.employee_id == Employee.id)  # Присоединяем таблицу State
                    .filter(
                        State.department_id == management.department_id,
                        State.management_id == management.id,
                    )  # Фильтруем по департаменту и управлению
                    .filter(Status.id == status.id)  # Фильтруем по id статуса
                    .count()
                )
                # Добавляем статус в словарь
                management_data[status.nameEN] = {"count": count, "name": status.nameRU}

                # Выполняем запрос для получения сотрудников с управлением и статусом
                employees_by_management_and_status = (
                    db.query(
                        Management.id.label("management_id"),
                        Management.nameRU,
                        Status.id.label("status_id"),
                        Status.nameRU,
                        Employee.id.label("employee"),
                        Employee.firstname,
                        Employee.surname
                    )
                    .join(Employee, Employee.management_id == Management.id)
                    .join(status_employee_association, Employee.id == status_employee_association.c.employee_id)
                    .join(Status, Status.id == status_employee_association.c.status_id)
                    .all()
                )

                # Группируем результат вручную по управлению и статусу
                grouped_data = defaultdict(lambda: {"employees": [], "count": 0})

                for management_id, nameRU, status_id, nameRU, employee_id, firstname, surname in employees_by_management_and_status:
                    grouped_data[(management, status)]["employees"].append(f"{firstname} {surname}")
                    grouped_data[(management, status)]["count"] += 1

                # Вывод данных
                for (management, status), data in grouped_data.items():
                    print(f"Управление: {management}, Статус: {status}")
                    print(f"Количество сотрудников: {data['count']}")
                    print("Список сотрудников:")
                    for employee in data["employees"]:
                        print(f"- {employee}")
                    print()

                    # Добавляем статус в словарь
                    management_data[f"list_{status.nameEN}"] = {
                        "surnames": [status_employee.surname for status_employee in status_list],
                        "start_data": status.start_date,
                        "end_data": status.end_date
                    }
                print(management_data)
            # Добавляем информацию по каждому управлению в итоговый словарь
            result[management.nameKZ] = management_data

        # Добавляем общее количество в итоговый словарь
        result["Жалпы есеп"] = overall_count

        return result

    def create_word_report_from_template(self, db: Session, user_id: int):
        """
        Создание отчета Word с подстановкой данных из функции get_count_of_state и get_count_of_management_state.
        """
        # Получаем данные из функции get_count_of_management_state
        management_data = self.get_count_of_management_state(db, user_id)

        # Получаем текущую дату в формате день.месяц.год
        current_date = datetime.now().strftime("%d.%m.%Y")

        file_path = './template.docx'
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден. Пожалуйста, проверьте путь к файлу.")

        doc = Document(file_path)

        # Изменяем первый параграф (перед таблицей)
        first_paragraph = doc.paragraphs[0]  # Получаем первый параграф документа
        # Вставляем текст с датой
        run = first_paragraph.add_run(f"ЖЕТІНШІ ДЕПАРТАМЕНТ ЖЕКЕ ҚҰРАМЫНЫҢ САПТЫҚ ТІЗІМІ {current_date} ЖЫЛҒЫ")
        # Применяем стиль к тексту (Times New Roman, размер 12)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.bold = True  # Делаем текст жирным
        # Настройка выравнивания по центру
        first_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Поиск таблицы в документе
        table = doc.tables[0]  # Предположим, что нужная таблица первая

        # Заполнение таблицы данными по каждому управлению
        row_idx = 2  # Строка для первого управления

        # Получаем общее количество строк в таблице
        total_rows = len(table.rows)

        for management_name, management_info in management_data.items():
            row = table.rows[row_idx]
            row.cells[1].text = management_name  # Название управления

            # Заполняем данные по каждому статусу для этого управления
            management_values = [
                str(management_info.get("by state", {}).get("count", 0)),
                str(management_info.get("by list", {}).get("count", 0)),
                str(management_info.get("by vacant", {}).get("count", 0)),
                str(management_info.get("inline", {}).get("count", 0)),
                str(management_info.get("on duty", {}).get("count", 0)),
                str(management_info.get("after duty", {}).get("count", 0)),
                str(management_info.get("business trip", {}).get("count", 0)),
                str(management_info.get("on studying", {}).get("count", 0)),
                str(management_info.get("on leave", {}).get("count", 0)),
                str(management_info.get("on sick leave", {}).get("count", 0)),
                str(management_info.get("out seconded", {}).get("count", 0)),
                str(management_info.get("on seconded", {}).get("count", 0))
            ]

            # Заполнение значений в ячейки таблицы
            for i, value in enumerate(management_values, start=2):  # Начинаем с ячейки 2
                cell = row.cells[i]
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
                # Для выравнивания по обеим сторонам (center)
                tcVAlign.set(qn('w:val'), 'center')
                tcPr.append(tcVAlign)

            # Сделать жирным последнюю строку
            if row_idx == total_rows - 1:  # Если это последняя строка
                for cell in row.cells:
                    paragraph = cell.paragraphs[0]
                    run = paragraph.runs[0]
                    run.bold = True  # Делаем весь текст в строке жирным

            row_idx += 1

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        return buffer


state_service = StateService(State)
