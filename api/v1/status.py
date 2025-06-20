from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from core import get_db

from schemas import StatusRead, StatusUpdate, StatusCreate
from schemas.employee_status import BulkStatusUpdateRequestSchema, BulkStatusUpdateResponseSchema
from services import status_service, employee_service
# Assuming TokenData and get_current_token_data are not directly needed here if dependency handles it
from api.v1.dependencies import check_bulk_status_update_permissions # Import new dependency

router = APIRouter(prefix="/statuses", tags=["Statuses"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[StatusRead],
    summary="Статусы",
)
async def get_all(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all Statuses

    """

    return status_service.get_multi(db, skip, limit)


@router.post(
    "",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_201_CREATED,
    response_model=StatusRead,
    summary="Create Position",
)
async def create(
    *,
    db: Session = Depends(get_db),
    body: StatusCreate,
):
    """
    Create Status

    - **name**: required
    """

    return status_service.create(db, body)


@router.get(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=StatusRead,
    summary="Get Status by id",
)
async def get_by_id(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Get Status by id

    - **id**: UUID - required.
    """

    return status_service.get_by_id(db, str(id))


@router.put(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=StatusRead,
    summary="Update Status",
)
async def update(
    *,
    db: Session = Depends(get_db),
    id: str,
    body: StatusUpdate,
):
    """
    Update Status

    """

    return status_service.update(
        db, db_obj=status_service.get_by_id(db, str(id)), obj_in=body
    )


@router.delete(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Status",
)
async def delete(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Delete Status

    - **id**: UUId - required
    """

    status_service.remove(db, str(id))


@router.post(
    "/bulk",
    response_model=BulkStatusUpdateResponseSchema,
    summary="Bulk update employee statuses",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(check_bulk_status_update_permissions)] # Added dependency
)
def bulk_update_statuses_endpoint(
    request_data: BulkStatusUpdateRequestSchema, # request_data is passed to the dependency by FastAPI
    db: Session = Depends(get_db)
    # token_data: TokenData = Depends(get_current_token_data) # No longer needed directly
):
    # This service method is synchronous
    # The dependency check_bulk_status_update_permissions runs before this.
    # request_data is automatically passed to the dependency by FastAPI due to matching name and type hint.
    response = employee_service.bulk_update_employee_statuses(db=db, request_data=request_data)
    return response
