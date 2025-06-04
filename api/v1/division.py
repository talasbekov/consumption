# app/api/v1/division.py

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core import get_db
from schemas import DivisionRead, DivisionUpdate, DivisionCreate
from services import division_service

router = APIRouter(prefix="/api/v1/divisions", tags=["Divisions"])


@router.get(
    "",
    response_model=List[DivisionRead],
    summary="Get all Divisions",
)
async def get_all(
    *,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all Divisions
    """
    divisions = await division_service.get_multi(db, skip, limit)
    return divisions


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DivisionRead,
    summary="Create Division",
)
async def create_division(
    *,
    db: AsyncSession = Depends(get_db),
    body: DivisionCreate,
):
    """
    Create Division

    - **name**: required
    """
    new_division = await division_service.create(db, body)
    return new_division


@router.get(
    "/{id}/",
    response_model=DivisionRead,
    summary="Get Division by id",
)
async def get_by_id(
    *,
    db: AsyncSession = Depends(get_db),
    id: str,
):
    """
    Get Division by id

    - **id**: UUID - required.
    """
    division = await division_service.get(db, id)
    return division


@router.put(
    "/{id}/",
    response_model=DivisionRead,
    summary="Update Division",
)
async def update_division(
    *,
    db: AsyncSession = Depends(get_db),
    id: str,
    body: DivisionUpdate,
):
    """
    Update Division
    """
    db_obj = await division_service.get(db, id)
    updated = await division_service.update(db, db_obj=db_obj, obj_in=body)
    return updated


@router.delete(
    "/{id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Division",
)
async def delete_division(
    *,
    db: AsyncSession = Depends(get_db),
    id: str,
):
    """
    Delete Division

    - **id**: UUID - required
    """
    await division_service.remove(db, id)
    return None


@router.get(
    "/department/directorate/count",
    response_model=List[dict],
    summary="Get employee count by directorate",
)
async def get_employee_count_by_directorate(
    db: AsyncSession = Depends(get_db),
):
    """
    Расход сотрудников всего департамента
    """
    result = await division_service.get_count_state(db)
    return result
