from io import BytesIO
from pathlib import Path
from typing import List

import aiofiles
from fastapi import APIRouter, Depends, status, UploadFile, HTTPException
from fastapi.security import HTTPBearer
from fastapi_jwt_auth import AuthJWT

from sqlalchemy.orm import Session
import pandas as pd
from PIL import Image

from core import get_db
from models import Employee
# from models import Employee
from schemas import EmployeeRead, EmployeeUpdate, EmployeeCreate
from services import employee_service

router = APIRouter(prefix="/employees", tags=["Employees"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[EmployeeRead],
    summary="Get all Employees",
)
async def get_all(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 200,
):
    """
    Get all Employees

    """

    return employee_service.get_multi(db, skip, limit)


@router.post(
    "",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeRead,
    summary="Create Position",
)
async def create(
    *,
    db: Session = Depends(get_db),
    body: EmployeeCreate,
):
    """
    Create Employee

    - **name**: required
    """

    return employee_service.create(db, body)


@router.get(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=EmployeeRead,
    summary="Get Employee by id",
)
async def get_by_id(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Get Employee by id

    - **id**: UUID - required.
    """

    return employee_service.get_by_id(db, str(id))


@router.put(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=EmployeeRead,
    summary="Update Employee",
)
async def update(
    *,
    db: Session = Depends(get_db),
    id: str,
    body: EmployeeUpdate,
):
    """
    Update Employee

    """

    return employee_service.update(
        db, db_obj=employee_service.get_by_id(db, str(id)), obj_in=body
    )


@router.delete(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Employee",
)
async def delete(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Delete Employee

    - **id**: UUId - required
    """

    employee_service.remove(db, str(id))


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[EmployeeRead],
    summary="Get all Employees",
)
async def get_all_employee_by_state(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all Employees
    """

    return employee_service.get_multi(db, skip, limit)


# Эндпоинт для загрузки Excel файла
@router.post("/upload-excel/")
async def upload_excel(file: UploadFile, directory: str, db: Session = Depends(get_db)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file in .xlsx format.")

    try:
        # Читаем содержимое файла
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), engine="openpyxl", converters={"ИИН": lambda x: str(x).zfill(12)})
        df.columns = [col.strip() for col in df.columns]

        # Проверяем обязательные столбцы
        required_columns = ["Фамилия", "Имя", "Отчество", "ИИН"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing_columns)}")

        # Заменяем NaN на None
        df = df.where(pd.notnull(df), None)

        # Путь к папке с фотографиями
        # directory = "./media/images/fotoforportal"
        photo_directory = Path(directory).resolve(strict=True)
        if not photo_directory.exists() or not photo_directory.is_dir():
            raise HTTPException(status_code=400, detail=f"Directory '{directory}' does not exist or is not a directory")

        # Вставка данных в базу
        for _, row in df.iterrows():
            try:
                if not row["ИИН"]:
                    raise HTTPException(status_code=400, detail=f"Invalid IIN at row {_}")

                # Проверяем наличие фотографии
                iin = str(row["ИИН"])
                photo_path = photo_directory / f"{iin}.JPG"
                photo_url = None
                print(f"Processing IIN: {iin}, looking for photo: {photo_path}")

                if photo_path.exists():
                    # Используем aiofiles для асинхронного чтения файла
                    async with aiofiles.open(photo_path, 'rb') as file:
                        file_contents = await file.read()

                    # Открываем изображение через PIL
                    try:
                        image = Image.open(BytesIO(file_contents))
                        print(f"Photo found for IIN: {iin}")
                    except Exception as e:
                        print(f"Error opening image for IIN {iin}: {e}")
                        continue

                    # Преобразуем RGBA в RGB, если нужно
                    if image.mode == "RGBA":
                        image = image.convert("RGB")

                    # Обрезка изображения до соотношения сторон 3x4
                    try:
                        image = employee_service.crop_to_aspect_ratio(image, 3, 4)
                        print(f"Photo cropped for IIN: {iin}")
                    except Exception as e:
                        print(f"Error cropping image for IIN {iin}: {e}")
                        continue

                    # Сохраняем обработанное изображение
                    processed_photo_path = photo_directory / f"{iin}.JPG"
                    try:
                        image.save(processed_photo_path)
                        photo_url = f"/media/images/fotoforportal/{iin}.JPG"
                        print(f"Processed photo saved for IIN: {iin}")
                    except Exception as e:
                        print(f"Error saving processed image for IIN {iin}: {e}")
                        continue

                else:
                    print(f"Photo not found for IIN: {iin}")

                # Добавляем или обновляем запись сотрудника
                employee = Employee(
                    surname=row["Фамилия"],
                    firstname=row["Имя"],
                    patronymic=row["Отчество"],
                    iin=iin,
                    sort=0,
                    rank_id=1,  # Пример, значение по умолчанию
                    photo=photo_url,  # Сохраняем путь к фотографии
                )
                db.add(employee)

            except Exception as e:
                print(f"Error processing row {row}: {e}")

        # Сохраняем изменения
        db.commit()
        return {"message": "File processed successfully", "rows": len(df)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")

@router.post(
    "/bulk/upload/photos/for/employee/states/",
    summary="Bulk update Employee's photos for employee states"
    )
async def upload_photos_to_employees(*, directory: str, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    return await employee_service.upload_photos_to_employees(db, directory, user_id)
