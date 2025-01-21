import logging
from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException, Response, Body
from fastapi.security import HTTPBearer
from fastapi_jwt_auth import AuthJWT


from sqlalchemy.orm import Session

from core import get_db

from schemas import StateRead, StateUpdate, StateCreate, EmployeeDataBulkUpdate, EmployeeStateRead
from services import state_service, employee_service

router = APIRouter(prefix="/states", tags=["States"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[StateRead],
    summary="Штатка",
)
async def get_all(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 500,
):
    """
    Get all States

    """

    return state_service.get_multi(db, skip, limit)


@router.post(
    "",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_201_CREATED,
    response_model=StateRead,
    summary="Create State",
)
async def create(
    *,
    db: Session = Depends(get_db),
    body: StateCreate,
):
    """
    Create State

    - **name**: required
    """

    return state_service.create(db, body)


@router.get(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=StateRead,
    summary="Get State by id",
)
async def get_by_id(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Get State by id

    - **id**: UUID - required.
    """

    return state_service.get_by_id(db, str(id))


@router.put(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=StateRead,
    summary="Update State",
)
async def update(
    *,
    db: Session = Depends(get_db),
    id: str,
    body: StateUpdate,
):
    """
    Update State

    """

    return state_service.update(
        db, db_obj=state_service.get_by_id(db, str(id)), obj_in=body
    )


@router.delete(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete State",
)
async def delete(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Delete State

    - **id**: UUId - required
    """

    state_service.remove(db, str(id))


@router.get(
    "/count",
    dependencies=[Depends(HTTPBearer())],
    summary="Количественный свод статусов",
)
async def get_all_counts(
    *,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    """
    Get all States

    """
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()

    return state_service.get_count_of_state(db, user_id)


@router.get(
    "/management/count",
    dependencies=[Depends(HTTPBearer())],
    summary="Get all Management count",
)
async def get_count_of_management_state(
    *,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    """
    Get all States

    """
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()

    return state_service.get_count_of_management_state(db, user_id)


@router.get(
    "/in/management",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[EmployeeStateRead],
    summary="Get all Employees by Management",
)
async def get_employees_by_management(
        *,
        db: Session = Depends(get_db),
        Authorize: AuthJWT = Depends()
):
    """
    Get all States
    """
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    return await employee_service.get_employees_by_management(db, user_id)


@router.post(
    "/in/management/upload/photo",
    dependencies=[Depends(HTTPBearer())],
    summary="Upload photos for Employees",
)
async def upload_photo(
        *,
        db: Session = Depends(get_db),
        photos: List[UploadFile] = File(...),
        employee_ids: str = Form(...),  # Ожидаем employee_ids как строку через Form
        Authorize: AuthJWT = Depends()
):
    """
    Upload photos for specific Employees
    """
    Authorize.jwt_required()

    # Логируем полученные данные для отладки
    print(f"Received employee_ids (raw): {employee_ids}")

    # Преобразуем строку employee_ids в список целых чисел
    try:
        # Разделяем строку по запятым и преобразуем каждое значение в int
        employee_ids_list = [int(e_id.strip()) for e_id in employee_ids.split(",")]

        # Проверяем, пуст ли список
        if not employee_ids_list:
            raise ValueError("Employee IDs list is empty")

    except ValueError as e:
        # Логирование ошибки для отладки
        print(f"Error converting employee_ids: {str(e)}")
        raise HTTPException(status_code=422, detail="One or more employee_ids are not valid integers")

    # Логирование для отладки
    print(f"Processed employee_ids: {employee_ids_list}")
    print(f"Received {len(photos)} photos")

    # Проверяем соответствие количества фотографий и employee_ids
    if len(photos) != len(employee_ids_list):
        print(f"Количество фотографий ({len(photos)}) не совпадает с количеством employee_ids ({len(employee_ids_list)})")
        raise HTTPException(status_code=400, detail="The number of employees and photos does not match")

    # Передаем фотографии в сервис для обработки
    return await employee_service.upload_only_photos(db, employee_ids_list, photos)


@router.post(
    "/in/management/upload/data",
    dependencies=[Depends(HTTPBearer())],
    summary="Upload data for Employees",
)
async def upload_data(
    *,
    db: Session = Depends(get_db),
    employee_data: List[EmployeeDataBulkUpdate] = Body(...),  # Принимаем JSON
    Authorize: AuthJWT = Depends()
):
    """
    Upload data for all Employees in a management group
    """
    Authorize.jwt_required()

    # Логирование пользователя
    current_user = Authorize.get_jwt_subject()
    logging.info(f"User {current_user} is uploading employee data")

    # Передаем данные в сервис для обновления сотрудников
    try:
        await state_service.update_employees_by_state(db, employee_data)
        return {"message": "Employees updated successfully"}
    except HTTPException as e:
        logging.error(f"Error updating employees: {e.detail}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")



# FastAPI эндпоинт для выгрузки документа
@router.get("/download-word", dependencies=[Depends(HTTPBearer())])
def download_word_report(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    # Создаем Word документ
    word_file = state_service.create_word_report_from_template(db, user_id)

    # Отправляем документ как файл
    return Response(content=word_file.read(),
                    media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    headers={"Content-Disposition": "attachment; filename=report.docx"})


