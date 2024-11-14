from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from core import get_db

from schemas import RankRead, RankUpdate, RankCreate
from services import rank_service

router = APIRouter(prefix="/ranks", tags=["Ranks"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[RankRead],
    summary="Get all Ranks",
)
async def get_all(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all Ranks

    """

    return rank_service.get_multi(db, skip, limit)


@router.post(
    "",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_201_CREATED,
    response_model=RankRead,
    summary="Create Rank",
)
async def create(
    *,
    db: Session = Depends(get_db),
    body: RankCreate,
):
    """
    Create Rank

    - **name**: required
    """

    return rank_service.create(db, body)


@router.get(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=RankRead,
    summary="Get Rank by id",
)
async def get_by_id(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Get Rank by id

    - **id**: UUID - required.
    """

    return rank_service.get_by_id(db, str(id))


@router.put(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=RankRead,
    summary="Update Rank",
)
async def update(
    *,
    db: Session = Depends(get_db),
    id: str,
    body: RankUpdate,
):
    """
    Update Rank

    """

    return rank_service.update(
        db, db_obj=rank_service.get_by_id(db, str(id)), obj_in=body
    )


@router.delete(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Rank",
)
async def delete(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Delete Rank

    - **id**: UUId - required
    """

    rank_service.remove(db, str(id))

