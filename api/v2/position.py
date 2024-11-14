from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from core import get_db

from schemas import PositionRead, PositionUpdate, PositionCreate
from services import position_service

router = APIRouter(prefix="/positions", tags=["Positions"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[PositionRead],
    summary="Get all Positions",
)
async def get_all(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all Positions

    """

    return position_service.get_multi(db, skip, limit)


@router.post(
    "",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_201_CREATED,
    response_model=PositionRead,
    summary="Create Position",
)
async def create(
    *,
    db: Session = Depends(get_db),
    body: PositionCreate,
):
    """
    Create Position

    - **name**: required
    """

    return position_service.create(db, body)


@router.get(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=PositionRead,
    summary="Get Position by id",
)
async def get_by_id(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Get Position by id

    - **id**: UUID - required.
    """

    return position_service.get_by_id(db, str(id))


@router.put(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=PositionRead,
    summary="Update Position",
)
async def update(
    *,
    db: Session = Depends(get_db),
    id: str,
    body: PositionUpdate,
):
    """
    Update Position

    """

    return position_service.update(
        db, db_obj=position_service.get_by_id(db, str(id)), obj_in=body
    )


@router.delete(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Position",
)
async def delete(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Delete Position

    - **id**: UUId - required
    """

    position_service.remove(db, str(id))

