from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from core import get_db

from schemas import EmployerRead, EmployerUpdate, EmployerCreate
from services import employer_service

router = APIRouter(prefix="/employers", tags=["Employers"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[EmployerRead],
    summary="Get all Employers",
)
async def get_all(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 200,
):
    """
    Get all Employers

    """

    return employer_service.get_multi(db, skip, limit)


@router.post(
    "",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_201_CREATED,
    response_model=EmployerRead,
    summary="Create Position",
)
async def create(
    *,
    db: Session = Depends(get_db),
    body: EmployerCreate,
):
    """
    Create Employer

    - **name**: required
    """

    return employer_service.create(db, body)


@router.get(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=EmployerRead,
    summary="Get Employer by id",
)
async def get_by_id(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Get Employer by id

    - **id**: UUID - required.
    """

    return employer_service.get_by_id(db, str(id))


@router.put(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=EmployerRead,
    summary="Update Employer",
)
async def update(
    *,
    db: Session = Depends(get_db),
    id: str,
    body: EmployerUpdate,
):
    """
    Update Employer

    """

    return employer_service.update(
        db, db_obj=employer_service.get_by_id(db, str(id)), obj_in=body
    )


@router.delete(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Employer",
)
async def delete(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Delete Employer

    - **id**: UUId - required
    """

    employer_service.remove(db, str(id))


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[EmployerRead],
    summary="Get all Employers",
)
async def get_all_emp_by_state(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all Employers
    """

    return employer_service.get_multi(db, skip, limit)
