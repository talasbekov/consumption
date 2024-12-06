from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from core import get_db

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
