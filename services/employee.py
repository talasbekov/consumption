import aiofiles

from models import (
    Employee, State, Department, Management, Division
)  # Предполагается, что у вас есть модель Employee в models.py
from schemas import (
    EmployeeCreate,
    EmployeeUpdate, StateRandomCreate,
)  # Предполагается, что у вас есть схемы создания и обновления событий

from services import user_service, data_service

from pathlib import Path
from typing import List, Type

from fastapi import UploadFile, HTTPException
from PIL import Image, ImageOps
from io import BytesIO

from sqlalchemy.orm import Session, joinedload

from services.base import ServiceBase
from schemas import EmployeeDataBulkUpdate



class EmployeeService(ServiceBase[Employee, EmployeeCreate, EmployeeUpdate]):

    async def upload_only_photos(
            self, db: Session, employee_ids: List[int], photos: List[UploadFile]
    ) -> list[Type[Employee]]:
        employees = []

        for employee_id, photo in zip(employee_ids, photos):
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                print(f"Работодатель с employee_id {employee_id} не найден")
                continue

            file_location = Path(f"media/images/employee_photos/{employee.iin}.jpg")
            file_location.parent.mkdir(parents=True, exist_ok=True)

            # Чтение и обработка изображения
            file_contents = await photo.read()
            image = Image.open(BytesIO(file_contents))

            # Проверка режима изображения
            if image.mode == "RGBA":
                image = image.convert("RGB")  # Преобразуем в RGB

            # Обрезка изображения до соотношения сторон 3x4
            image = self.crop_to_aspect_ratio(image, 3, 4)

            # Сохранение изображения
            image.save(file_location, format="JPEG", quality=85)

            # Обновляем путь к фотографии
            employee.photo = str(file_location)
            db.add(employee)
            employees.append(employee)

        # Сохраняем изменения в БД
        db.commit()

        # Обновляем данные работодателей
        for employee in employees:
            db.refresh(employee)

        return employees

    def crop_to_aspect_ratio(self, image: Image.Image, target_width_ratio: int,
                             target_height_ratio: int) -> Image.Image:
        # Вычисление целевого соотношения сторон
        target_ratio = target_width_ratio / target_height_ratio

        # Определяем текущие размеры изображения
        current_width, current_height = image.size
        current_ratio = current_width / current_height

        if current_ratio > target_ratio:
            # Изображение слишком широкое, обрезаем по ширине
            new_width = int(current_height * target_ratio)
            left = (current_width - new_width) // 2
            right = left + new_width
            image = image.crop((left, 0, right, current_height))
        else:
            # Изображение слишком высокое, обрезаем по высоте
            new_height = int(current_width / target_ratio)
            top = (current_height - new_height) // 2
            bottom = top + new_height
            image = image.crop((0, top, current_width, bottom))

        return ImageOps.fit(image, (target_width_ratio * 100, target_height_ratio * 100), Image.Resampling.LANCZOS)

    async def upload_only_data(
            self, db: Session, employee_data_list: List[EmployeeDataBulkUpdate]
    ) -> List[Employee]:
        employees = []

        for employee_data in employee_data_list:
            employee = db.query(Employee).filter(Employee.id == employee_data.employee_id).first()
            if not employee:
                print(f"Работодатель с employee_id {employee_data.employee_id} не найден")
                continue

            # Обновляем поля работодателя
            if employee_data.rank_id is not None:
                employee.rank_id = employee_data.rank_id
            if employee_data.status_id is not None:
                employee.status_id = employee_data.status_id
            if employee_data.sort is not None:
                employee.sort = employee_data.sort

            db.add(employee)
            employees.append(employee)

        # Сохраняем изменения в БД
        db.commit()

        # Обновляем данные работодателей
        for employee in employees:
            db.refresh(employee)

        return employees

    async def get_employees_by_management(self, db: Session, user_id: int):
        # Получаем пользователя
        user = user_service.get_by_id(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Получаем работодателя
        employee = employee_service.get_by_id(db, user.employee_id)

        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Получаем state для данного пользователя
        state = db.query(State).filter(State.employee_id == user.employee_id).first()

        if not state:
            raise HTTPException(status_code=404, detail="State not found for the employee")

        # Получаем работодателей, относящихся к тому же управлению
        employees = db.query(Employee).join(State).options(
            joinedload(Employee.states)  # Это загружает связанные объекты сразу
        ).filter(
            State.management_id == state.management_id,
            State.division_id.isnot(None)
        ).all()
        for emp in employees:
            print(emp.states)
            for st in emp.states:
                print(st.id)

        return employees

    async def create_employee_states(self, db: Session):
        # Предзагрузка данных
        employees = db.query(Employee).all()
        department = db.query(Department).first()

        if not department:
            print("Отдел отсутствует. Завершение операции.")
            return

        managements = db.query(Management).filter(Management.department_id == department.id).all()
        if not managements:
            print("Управления отсутствуют. Завершение операции.")
            return

        management_count = len(managements)
        if management_count == 0:
            print("Нет доступных управлений для распределения сотрудников. Завершение.")
            return

        employee_index = 0  # Индекс для распределения сотрудников

        for management in managements:
            # Получаем подразделения для текущего управления
            divisions = db.query(Division).filter(Division.management_id == management.id).all()

            if divisions:
                # Распределение сотрудников между подразделениями
                for division in divisions:
                    if employee_index >= len(employees):
                        break

                    # Выбираем сотрудника для текущего подразделения
                    employee = employees[employee_index]
                    employee_index += 1

                    # Создаем данные для state
                    state_data = StateRandomCreate(
                        department_id=department.id,
                        management_id=management.id,
                        division_id=division.id,
                        position_id=1,
                        employee_id=employee.id
                    )

                    # Создаем запись state
                    created_state = data_service.create_state(db, state_data)
                    if created_state is None:
                        print(
                            f"Ошибка при создании state для сотрудника {employee.id} в подразделении {division.id}. Пропуск.")
            else:
                # Если управление не имеет подразделений, назначаем сотрудников напрямую
                if employee_index >= len(employees):
                    break

                employee = employees[employee_index]
                employee_index += 1

                state_data = StateRandomCreate(
                    department_id=department.id,
                    management_id=management.id,
                    division_id=None,  # Нет подразделения
                    position_id=1,
                    employee_id=employee.id
                )

                created_state = data_service.create_state(db, state_data)
                if created_state is None:
                    print(
                        f"Ошибка при создании state для сотрудника {employee.id} в управлении {management.id}. Пропуск.")

        # Проверка на оставшихся сотрудников
        if employee_index < len(employees):
            print(f"Не удалось распределить {len(employees) - employee_index} сотрудников.")

        print("Распределение сотрудников завершено.")

    async def upload_photos_to_employees(self, db: Session, directory: str, user_id: int):
        # Получаем пользователя по ID
        user = user_service.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Проверяем state пользователя
        state = db.query(State).filter(State.employee_id == user.employee_id).first()
        if not state:
            raise HTTPException(status_code=404, detail="State not found for the employee")

        # Получаем список сотрудников по department_id
        states = db.query(State).filter(State.department_id == state.department_id).all()
        employee_list = [
            employee_service.get_by_id(db, st.employee_id) for st in states if st.employee_id
        ]

        # Проверяем директорию
        photo_directory = Path(directory).resolve(strict=True)
        if not photo_directory.exists() or not photo_directory.is_dir():
            raise HTTPException(status_code=400, detail=f"Directory '{directory}' does not exist or is not a directory")

        for employee in employee_list:
            if not employee or not employee.iin:
                print(f"Skipping invalid employee or missing IIN: {employee}")
                continue

            iin = employee.iin.strip()
            photo_path = photo_directory / f"{iin}.JPG"
            if not photo_path.exists():
                print(f"Photo not found for IIN: {iin}")
                continue

            # Асинхронное чтение файла
            async with aiofiles.open(photo_path, 'rb') as file:
                file_contents = await file.read()

            try:
                # Открываем и обрабатываем изображение
                image = Image.open(BytesIO(file_contents))
                if image.mode == "RGBA":
                    image = image.convert("RGB")

                # Обрезка до соотношения 3:4
                image = self.crop_to_aspect_ratio(image, 3, 4)

                # Сохранение обработанного изображения
                processed_photo_path = photo_directory / f"processed_{iin}.JPG"
                image.save(processed_photo_path)

                # Обновление записи сотрудника
                employee.photo = f"/media/images/fotoforportal/processed_{iin}.JPG"
                db.commit()
                print(f"Photo URL updated for IIN: {iin}")
            except Exception as e:
                db.rollback()
                print(f"Error processing photo for IIN {iin}: {e}")


employee_service = EmployeeService(Employee)
