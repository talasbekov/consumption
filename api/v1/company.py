from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from core import get_db

from schemas import CompanyRead, CompanyUpdate, CompanyCreate
from services import company_service

router = APIRouter(prefix="/company", tags=["Companies"], dependencies=[Depends(HTTPBearer())])


@router.get(
    "",
    dependencies=[Depends(HTTPBearer())],
    response_model=List[CompanyRead],
    summary="Get all Companies",
)
async def get_all(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all Companies

    """

    return company_service.get_multi(db, skip, limit)


@router.post(
    "",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_201_CREATED,
    response_model=CompanyRead,
    summary="Create Position",
)
async def create(
    *,
    db: Session = Depends(get_db),
    body: CompanyCreate,
):
    """
    Create Company

    - **name**: required
    """

    return company_service.create(db, body)


@router.get(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=CompanyRead,
    summary="Get Company by id",
)
async def get_by_id(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Get Company by id

    - **id**: Integer - required.
    """

    return company_service.get_by_id(db, str(id))


@router.put(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    response_model=CompanyRead,
    summary="Update Company",
)
async def update(
    *,
    db: Session = Depends(get_db),
    id: str,
    body: CompanyUpdate,
):
    """
    Update Company

    """

    return company_service.update(
        db, db_obj=company_service.get_by_id(db, str(id)), obj_in=body
    )


@router.delete(
    "/{id}/",
    dependencies=[Depends(HTTPBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Company",
)
async def delete(
    *,
    db: Session = Depends(get_db),
    id: str,
):
    """
    Delete Company

    - **id**: Integer - required
    """

    company_service.remove(db, str(id))
