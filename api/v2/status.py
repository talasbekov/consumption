from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from core import get_db

from schemas import StatusRead, StatusUpdate, StatusCreate
from services import status_service

router = APIRouter(prefix="/statuses", tags=["Statuses"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[StatusRead],
    summary="Get all Statuses",
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
