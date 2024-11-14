import json
from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException, Response
from fastapi.security import HTTPBearer
from fastapi_jwt_auth import AuthJWT
from pydantic.tools import parse_obj_as

from sqlalchemy.orm import Session

from core import get_db

from schemas import StateRead, StateUpdate, StateCreate, EmployerDataBulkUpdate, EmployerStateRead
from services import state_service, employer_service

router = APIRouter(prefix="/states", tags=["States"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[StateRead],
    summary="Get all States",
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
    summary="Get all States",
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
    "/in/management",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[EmployerStateRead],
    summary="Get all Employers by Management",
)
async def get_employers_by_management(
        *,
        db: Session = Depends(get_db),
        Authorize: AuthJWT = Depends()
):
    """
    Get all States
    """
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    return await employer_service.get_employers_by_management(db, user_id)


@router.post(
    "/in/management/upload/photo",
    dependencies=[Depends(HTTPBearer())],
    summary="Upload photos for Employers",
)
async def upload_photo(
        *,
        db: Session = Depends(get_db),
        photos: List[UploadFile] = File(...),
        employer_ids: str = Form(...),  # Ожидаем employer_ids как строку через Form
        Authorize: AuthJWT = Depends()
):
    """
    Upload photos for specific Employers
    """
    Authorize.jwt_required()

    # Логируем полученные данные для отладки
    print(f"Received employer_ids (raw): {employer_ids}")

    # Преобразуем строку employer_ids в список целых чисел
    try:
        # Разделяем строку по запятым и преобразуем каждое значение в int
        employer_ids_list = [int(e_id.strip()) for e_id in employer_ids.split(",")]

        # Проверяем, пуст ли список
        if not employer_ids_list:
            raise ValueError("Employer IDs list is empty")

    except ValueError as e:
        # Логирование ошибки для отладки
        print(f"Error converting employer_ids: {str(e)}")
        raise HTTPException(status_code=422, detail="One or more employer_ids are not valid integers")

    # Логирование для отладки
    print(f"Processed employer_ids: {employer_ids_list}")
    print(f"Received {len(photos)} photos")

    # Проверяем соответствие количества фотографий и employer_ids
    if len(photos) != len(employer_ids_list):
        raise HTTPException(status_code=400, detail="The number of employers and photos does not match")

    # Передаем фотографии в сервис для обработки
    return await employer_service.upload_only_photos(db, employer_ids_list, photos)


@router.post(
    "/in/management/upload/data",
    dependencies=[Depends(HTTPBearer())],
    summary="Upload data for Employers",
)
async def upload_data(
        *,
        db: Session = Depends(get_db),
        employer_data: str = Form(...),  # Ожидаем данные как строку через Form
        Authorize: AuthJWT = Depends()
):
    """
    Upload data for all Employers in a management group
    """
    Authorize.jwt_required()

    # Преобразуем строку employer_data в список объектов
    try:
        employer_data_list = parse_obj_as(List[EmployerDataBulkUpdate], json.loads(employer_data))
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Invalid JSON format in employer_data")

    # Передаем данные в сервис для обновления работодателей
    return await employer_service.upload_only_data(db, employer_data_list)


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


