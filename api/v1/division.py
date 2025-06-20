# app/api/v1/division.py

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core import get_db
from schemas import DivisionRead, DivisionUpdate, DivisionCreate
from schemas.auth import TokenData
from services import division_service
from api.v1.auth import get_current_token_data
from api.v1.dependencies import require_role # Added import

router = APIRouter(prefix="/api/v1/divisions", tags=["Divisions"])
# Note: The global router dependencies=[Depends(HTTPBearer())] from previous subtasks is missing here.
# It should be added if it's a global requirement.
# For now, applying dependency only to the specified endpoint.


@router.get(
    "",
    response_model=List[DivisionRead],
    summary="Get Divisions based on user role and assignment", # Updated summary
)
async def get_filtered_divisions( # Renamed function
    *,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    token_data: TokenData = Depends(get_current_token_data) # Added token data dependency
):
    """
    Get Divisions.
    - Admins (role 1, 4) get all divisions.
    - Department/Management Heads (role 2, 3) get divisions within their department hierarchy.
    """
    divisions = await division_service.get_divisions_for_user(
        db,
        user_role=token_data.role,
        user_assigned_division_id=token_data.division_id,
        skip=skip,
        limit=limit
    )
    return divisions


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DivisionRead,
    summary="Create Division",
    dependencies=[Depends(require_role([4]))] # Added role dependency
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
