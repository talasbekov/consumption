from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from core import get_db

from schemas import DivisionRead, DivisionUpdate, DivisionCreate
from services import division_service

router = APIRouter(prefix="/divisions", tags=["Divisions"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[DivisionRead],
    summary="Get all Divisions",
)
async def get_all(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all Divisions

    """

    return division_service.get_multi(db, skip, limit)


@router.post(
    "",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_201_CREATED,
    response_model=DivisionRead,
    summary="Create Position",
)
async def create(
    *,
    db: Session = Depends(get_db),
    body: DivisionCreate,
):
    """
    Create Division

    - **name**: required
    """

    return division_service.create(db, body)


@router.get(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=DivisionRead,
    summary="Get Division by id",
)
async def get_by_id(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Get Division by id

    - **id**: UUID - required.
    """

    return division_service.get_by_id(db, str(id))


@router.put(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=DivisionRead,
    summary="Update Division",
)
async def update(
    *,
    db: Session = Depends(get_db),
    id: str,
    body: DivisionUpdate,
):
    """
    Update Division

    """

    return division_service.update(
        db, db_obj=division_service.get_by_id(db, str(id)), obj_in=body
    )


@router.delete(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Division",
)
async def delete(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Delete Division

    - **id**: UUId - required
    """

    division_service.remove(db, str(id))


@router.get(
    "/department/directorate/count",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[dict]
)
def get_employer_count_by_directorate(db: Session = Depends(get_db)):
    """
    Расход сотрудников всего департамента
    """
    return division_service.get_count_state(db)

