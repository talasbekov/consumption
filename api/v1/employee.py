from io import BytesIO
from pathlib import Path
from typing import List

import aiofiles
from fastapi import APIRouter, Depends, status, UploadFile, HTTPException
from fastapi.security import HTTPBearer


from sqlalchemy.orm import Session
import pandas as pd
from PIL import Image

from core import get_db
from models import Employee
# from models import Employee
from schemas import EmployeeRead, EmployeeUpdate, EmployeeCreate, StatusUpdate
from schemas.employee_status import EmployeeStatusCreate, EmployeeStatusRead
from schemas.auth import TokenData
from services import employee_service
from api.v1.dependencies import require_role, check_role3_self_management_editor, check_role3_create_in_self_management # Added new dependency
from api.v1.auth import get_current_token_data

router = APIRouter(prefix="/employees", tags=["Employees"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    response_model=List[EmployeeRead],
    summary="Get employees based on user's scope", # Updated summary
)
async def get_all( # Function name is fine, summary clarifies its new behavior
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 200,
    token_data: TokenData = Depends(get_current_token_data) # Added token_data
):
    """
    Get Employees based on the calling user's role and division scope.
    Admins (role 1, 4) get all. Department/Management heads (role 2, 3) get from their department.
    """
    # Note: employee_service.get_employees_by_scope is synchronous.
    # FastAPI will run it in a threadpool because the endpoint is async.
    employees = employee_service.get_employees_by_scope(
        db, token_data=token_data, skip=skip, limit=limit
    )
    return employees


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeRead,
    summary="Create Employee",
    dependencies=[Depends(check_role3_create_in_self_management)] # Changed to specific dependency
)
async def create(
    *,
    db: Session = Depends(get_db), # This will be passed to the dependency by FastAPI if it needs it
    body: EmployeeCreate, # This will be passed to the dependency by FastAPI
    # token_data: TokenData = Depends(get_current_token_data) # No longer needed directly if dependency handles it
):
    """
    Create Employee. Access controlled by roles and management scope.

    - **name**: required
    """

    return employee_service.create(db, body)


@router.get(
    "/{id}/",
    response_model=EmployeeRead,
    summary="Get Employee by id (scoped)", # Updated summary
)
async def get_by_id(
    *,
    db: Session = Depends(get_db),
    id: str, # Should be int if employee_id is int
    token_data: TokenData = Depends(get_current_token_data) # Added token_data
):
    """
    Get Employee by id, subject to user's scope.
    Admins (role 1, 4) can get any. Others can only get if employee is in their department.
    """
    try:
        employee_id = int(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid employee ID format.")

    # Note: employee_service.get_employee_by_id_and_scope is synchronous.
    employee = employee_service.get_employee_by_id_and_scope(
        db, employee_id=employee_id, token_data=token_data
    )
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found or not accessible.")
    return employee


@router.put(
    "/{id}/",
    response_model=EmployeeRead,
    summary="Update Employee",
    dependencies=[Depends(check_role3_self_management_editor)] # Added specific dependency
)
async def update(
    *,
    db: Session = Depends(get_db),
    id: str, # Path param 'id' will be captured by FastApiPath('target_employee_id') in dependency
    body: EmployeeUpdate,
    # token_data: TokenData = Depends(get_current_token_data) # No longer needed directly if dependency handles it
):
    """
    Update Employee. Access controlled by roles and management scope.

    """

    return employee_service.update(
        db, db_obj=employee_service.get_by_id(db, str(id)), obj_in=body
    )


@router.delete(
    "/{id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Employee",
    # Keep role 4 for general delete, or enhance check_role3_self_management_editor if role 3 can delete
    # For this step, applying the new check, which means role 4 bypasses, role 3 is checked.
    dependencies=[Depends(check_role3_self_management_editor)]
)
async def delete(
    *,
    db: Session = Depends(get_db),
    id: str, # Path param 'id' will be captured by FastApiPath('target_employee_id') in dependency
    # token_data: TokenData = Depends(get_current_token_data) # No longer needed
):
    """
    Delete Employee. Access controlled by roles and management scope.

    - **id**: UUId - required
    """

    employee_service.remove(db, str(id))


# Removed duplicate GET /employees endpoint (get_all_employee_by_state)
# The first one named "get_all" is kept.

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

# @router.post(
#     "/bulk/upload/photos/for/employee/states/",
#     summary="Bulk update Employee's photos for employee states"
#     )
# async def upload_photos_to_employees(*, directory: str, db: Session = Depends(get_db)):
#     Authorize.jwt_required()
#     user_id = Authorize.get_jwt_subject()
#     return await employee_service.upload_photos_to_employees(db, directory, user_id)


@router.post(
    "/add/status/",
    response_model=EmployeeStatusRead, # Changed response model
    summary="Assign a status period to an employee", # Updated summary
    dependencies=[Depends(HTTPBearer())]
    )
async def assign_employee_status_endpoint( # Renamed function for clarity
        *,
        # employee_id: int, # Removed query parameter, employee_id is in EmployeeStatusCreate
        new_status_data: EmployeeStatusCreate,  # Changed request body type
        db: Session = Depends(get_db),
):
    # Service method is synchronous, removed await
    return employee_service.assign_employee_status(db=db, data=new_status_data)


@router.post(
    "/update/statuses/",
    summary="Update Employee's statuses"
    )
async def update_employees_statuses(*, db: Session = Depends(get_db)):
    return await employee_service.update_employees_statuses(db)
