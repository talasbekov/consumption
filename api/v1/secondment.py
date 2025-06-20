from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer # Assuming HTTPBearer is standard
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from core import get_db
from services import secondment_service # Assuming secondment_service is in services.__init__
from schemas.secondment import SecondmentLogRead
from schemas.auth import TokenData
from api.v1.auth import get_current_token_data
from api.v1.dependencies import ( # Import new dependencies
    check_initiate_secondment_permissions,
    check_request_return_permissions,
    check_approve_return_permissions
)

from pydantic import BaseModel # Keep for SecondmentInitiatePayload

class SecondmentInitiatePayload(BaseModel):
    employee_id: int
    target_division_id: int
    start_date: date
    expected_end_date: Optional[date] = None

router = APIRouter(
    prefix="/secondments",
    tags=["Secondments"],
    dependencies=[Depends(HTTPBearer())] # Standard auth dependency
)

@router.post(
    "/",
    response_model=SecondmentLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate a new employee secondment",
    dependencies=[Depends(check_initiate_secondment_permissions)] # Added dependency
)
def initiate_secondment_endpoint(
    payload: SecondmentInitiatePayload, # payload is passed to dependency by FastAPI
    db: Session = Depends(get_db),
    token_data: TokenData = Depends(get_current_token_data) # Still needed for initiating_user_id
):
    # The dependency check_initiate_secondment_permissions already ran.
    # It also receives 'payload' and 'token_data' implicitly from FastAPI.
    initiating_user_id = token_data.user_id

    new_secondment = secondment_service.initiate_secondment(
        db=db,
        employee_id=payload.employee_id,
        target_division_id=payload.target_division_id,
        start_date=payload.start_date,
        expected_end_date=payload.expected_end_date,
        initiating_user_id=initiating_user_id
    )
    return new_secondment

@router.patch(
    "/{secondment_id}/request-return",
    response_model=SecondmentLogRead,
    summary="Request the return of a seconded employee",
    dependencies=[Depends(check_request_return_permissions)] # Added dependency
)
def request_return_endpoint(
    secondment_id: int, # secondment_id is passed to dependency by FastAPI via Path(...)
    db: Session = Depends(get_db),
    token_data: TokenData = Depends(get_current_token_data) # Still needed for requesting_user_id
):
    # The dependency check_request_return_permissions already ran.
    requesting_user_id = token_data.user_id # Or dependency could return modified token_data/user
    updated_secondment = secondment_service.request_secondment_return(
        db=db,
        secondment_log_id=secondment_id,
        requesting_user_id=requesting_user_id
    )
    return updated_secondment

@router.patch(
    "/{secondment_id}/approve-return",
    response_model=SecondmentLogRead,
    summary="Approve the return of a seconded employee",
    dependencies=[Depends(check_approve_return_permissions)] # Added dependency
)
def approve_return_endpoint(
    secondment_id: int, # secondment_id is passed to dependency by FastAPI via Path(...)
    db: Session = Depends(get_db),
    token_data: TokenData = Depends(get_current_token_data) # Still needed for approving_user_id
):
    # The dependency check_approve_return_permissions already ran.
    approving_user_id = token_data.user_id
    approved_secondment = secondment_service.approve_secondment_return(
        db=db,
        secondment_log_id=secondment_id,
        approving_user_id=approving_user_id
    )
    return approved_secondment
