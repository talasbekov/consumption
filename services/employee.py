from models import (
    Employee, State
)  # Предполагается, что у вас есть модель Employee в models.py
from schemas import (
    EmployeeCreate,
    EmployeeUpdate,
)  # Предполагается, что у вас есть схемы создания и обновления событий

from services import user_service

from pathlib import Path
from typing import List

from fastapi import UploadFile, HTTPException
from PIL import Image, ImageOps
from io import BytesIO

from sqlalchemy.orm import Session, joinedload

from services.base import ServiceBase
from schemas import EmployeeDataBulkUpdate



class EmployeeService(ServiceBase[Employee, EmployeeCreate, EmployeeUpdate]):

    async def upload_only_photos(
            self, db: Session, employee_ids: List[int], photos: List[UploadFile]
    ) -> List[Employee]:
        employees = []

        for employee_id, photo in zip(employee_ids, photos):
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                print(f"Работодатель с employee_id {employee_id} не найден")
                continue

            file_location = Path(f"media/images/employee_photos/{employee.id}_{employee.surname}.jpg")
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


employee_service = EmployeeService(Employee)
