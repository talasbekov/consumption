from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from core import get_db

from schemas import ManagementRead, ManagementUpdate, ManagementCreate
from services import management_service

router = APIRouter(prefix="/managements", tags=["Managements"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[ManagementRead],
    summary="Get all Managements",
)
async def get_all(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all Managements

    """

    return management_service.get_multi(db, skip, limit)


@router.post(
    "",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_201_CREATED,
    response_model=ManagementRead,
    summary="Create Position",
)
async def create(
    *,
    db: Session = Depends(get_db),
    body: ManagementCreate,
):
    """
    Create Management

    - **name**: required
    """

    return management_service.create(db, body)


@router.get(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=ManagementRead,
    summary="Get Management by id",
)
async def get_by_id(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Get Management by id

    - **id**: UUID - required.
    """

    return management_service.get_by_id(db, str(id))


@router.put(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=ManagementRead,
    summary="Update Management",
)
async def update(
    *,
    db: Session = Depends(get_db),
    id: str,
    body: ManagementUpdate,
):
    """
    Update Management

    """

    return management_service.update(
        db, db_obj=management_service.get_by_id(db, str(id)), obj_in=body
    )


@router.delete(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Management",
)
async def delete(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Delete Management

    - **id**: UUId - required
    """

    management_service.remove(db, str(id))
