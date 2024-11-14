from models import (
    Employer, State
)  # Предполагается, что у вас есть модель Employer в models.py
from schemas import (
    EmployerCreate,
    EmployerUpdate,
)  # Предполагается, что у вас есть схемы создания и обновления событий

from services import user_service

from pathlib import Path
from typing import List

from fastapi import UploadFile, HTTPException
from PIL import Image
from io import BytesIO

from sqlalchemy.orm import Session, joinedload

from services.base import ServiceBase
from schemas import EmployerDataBulkUpdate



class EmployerService(ServiceBase[Employer, EmployerCreate, EmployerUpdate]):

    async def upload_only_photos(
            self, db: Session, employer_ids: List[int], photos: List[UploadFile]
    ) -> List[Employer]:
        employers = []

        for employer_id, photo in zip(employer_ids, photos):
            employer = db.query(Employer).filter(Employer.id == employer_id).first()
            if not employer:
                print(f"Работодатель с employer_id {employer_id} не найден")
                continue

            file_location = Path(f"media/images/employer_photos/{employer.id}_{employer.surname}.jpg")
            file_location.parent.mkdir(parents=True, exist_ok=True)

            # Чтение и обработка изображения
            file_contents = await photo.read()
            image = Image.open(BytesIO(file_contents))

            # Проверка режима изображения
            if image.mode == "RGBA":
                image = image.convert("RGB")  # Преобразуем в RGB

            # Сохранение изображения
            image.save(file_location)

            # Обновляем путь к фотографии
            employer.photo = str(file_location)
            db.add(employer)
            employers.append(employer)

        # Сохраняем изменения в БД
        db.commit()

        # Обновляем данные работодателей
        for employer in employers:
            db.refresh(employer)

        return employers

    async def upload_only_data(
            self, db: Session, employer_data_list: List[EmployerDataBulkUpdate]
    ) -> List[Employer]:
        employers = []

        for employer_data in employer_data_list:
            employer = db.query(Employer).filter(Employer.id == employer_data.employer_id).first()
            if not employer:
                print(f"Работодатель с employer_id {employer_data.employer_id} не найден")
                continue

            # Обновляем поля работодателя
            if employer_data.rank_id is not None:
                employer.rank_id = employer_data.rank_id
            if employer_data.status_id is not None:
                employer.status_id = employer_data.status_id
            if employer_data.sort is not None:
                employer.sort = employer_data.sort

            db.add(employer)
            employers.append(employer)

        # Сохраняем изменения в БД
        db.commit()

        # Обновляем данные работодателей
        for employer in employers:
            db.refresh(employer)

        return employers

    async def get_employers_by_management(self, db: Session, user_id: int):
        # Получаем пользователя
        user = user_service.get_by_id(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Получаем работодателя
        employer = employer_service.get_by_id(db, user.employer_id)

        if not employer:
            raise HTTPException(status_code=404, detail="Employer not found")

        # Получаем state для данного пользователя
        state = db.query(State).filter(State.employer_id == user.employer_id).first()

        if not state:
            raise HTTPException(status_code=404, detail="State not found for the employer")

        # Получаем работодателей, относящихся к тому же управлению
        employers = db.query(Employer).join(State).options(
            joinedload(Employer.states)  # Это загружает связанные объекты сразу
        ).filter(
            State.management_id == state.management_id,
            State.division_id.isnot(None)
        ).all()
        for emp in employers:
            print(emp.states)
            for st in emp.states:
                print(st.id)

        return employers


employer_service = EmployerService(Employer)
