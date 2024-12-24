from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from core import get_db

from schemas import DepartmentRead, DepartmentUpdate, DepartmentCreate
from services import department_service

router = APIRouter(prefix="/departments", tags=["Departments"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[DepartmentRead],
    summary="Get all Departments",
)
async def get_all(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all Departments

    """

    return department_service.get_multi(db, skip, limit)


@router.get(
    "/tree",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[DepartmentRead],
    summary="Get all Departments",
)
async def get_all_tree(
    *,
    db: Session = Depends(get_db)
):
    """
    Get all Departments

    """

    return department_service.get_all_tree(db)


@router.post(
    "",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_201_CREATED,
    response_model=DepartmentRead,
    summary="Create Position",
)
async def create(
    *,
    db: Session = Depends(get_db),
    body: DepartmentCreate,
):
    """
    Create Department

    - **name**: required
    """

    return department_service.create(db, body)


@router.get(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=DepartmentRead,
    summary="Get Department by id",
)
async def get_by_id(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Get Department by id

    - **id**: UUID - required.
    """

    return department_service.get_by_id(db, str(id))


@router.put(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=DepartmentRead,
    summary="Update Department",
)
async def update(
    *,
    db: Session = Depends(get_db),
    id: str,
    body: DepartmentUpdate,
):
    """
    Update Department

    """

    return department_service.update(
        db, db_obj=department_service.get_by_id(db, str(id)), obj_in=body
    )


@router.delete(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Department",
)
async def delete(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Delete Department

    - **id**: UUId - required
    """

    department_service.remove(db, str(id))

