from fastapi import HTTPException, status, Depends
from typing import List, Optional

# Assuming TokenData is in schemas.auth and get_current_token_data is in api.v1.auth
from schemas.auth import TokenData
from api.v1.auth import get_current_token_data

# Imports for potential future, more complex checks (not strictly needed for basic role_checker)
# from sqlalchemy.orm import Session
# from core import get_db
# from models import User, EmployeeStatus, Status, Employee


def require_role(allowed_roles: List[int]):
    """
    Dependency factory that creates a role checker.
    Checks if the current user's role (from token_data) is in the allowed_roles list.
    """
    async def role_checker(
        token_data: TokenData = Depends(get_current_token_data)
    ) -> TokenData: # Return TokenData for potential use in the endpoint
        if token_data.role is None: # Should ideally be caught by get_current_token_data
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role information is missing in the token."
            )
        if token_data.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions for this action." # Changed message slightly for clarity
            )
        return token_data
    return role_checker

# --- More specific dependencies ---
from fastapi import Path as FastApiPath # For path parameters in dependencies
from sqlalchemy.ext.asyncio import AsyncSession # Assuming async operations
from sqlalchemy import select
from datetime import date as python_date # To avoid conflict with models.Date if any

from models import User, Employee, Division, EmployeeStatus, Status, DivisionTypeEnum
from core import get_db # For AsyncSession

async def check_role3_self_management_editor(
    target_employee_id: int = FastApiPath(..., title="The ID of the employee to manage", description="ID of the target employee for the operation."),
    token_data: TokenData = Depends(get_current_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency to check if a Role 3 user (Management Head) can edit/delete an employee.
    Permissions:
    - Role 4 (Admin) can always edit.
    - Role 3 can edit if:
        - They are a manager of a 'Управление' (Directorate).
        - They are not currently 'Откомандирован' (SECONDED_OUT).
        - The target employee is within their own 'Управление'.
    """
    if token_data.role == 4: # Admin has full access
        return token_data

    if token_data.role != 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Role 3 required for this specific edit.")

    if not token_data.division_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not assigned to any management division.")

    user_s_management_division_result = await db.execute(select(Division).where(Division.id == token_data.division_id))
    user_s_management_division = user_s_management_division_result.scalar_one_or_none()

    if not user_s_management_division or user_s_management_division.division_type != DivisionTypeEnum.DIRECTORATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a manager of a 'Управление' (Directorate).")

    # Check if Role 3 user is "Откомандирован"
    user_object_result = await db.execute(select(User).where(User.id == token_data.user_id))
    user_object = user_object_result.scalar_one_or_none()
    if not user_object or not user_object.employee_id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User's employee record not found for status check.")

    status_otk_result = await db.execute(select(Status.id).filter(Status.code == "SECONDED_OUT"))
    status_otkomandirovan_id = status_otk_result.scalar_one_or_none()
    if not status_otkomandirovan_id: # This is a server configuration issue
        # Log this error server-side
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server configuration error: 'SECONDED_OUT' status code definition not found.")

    user_status_record_result = await db.execute(
        select(EmployeeStatus).where(
            EmployeeStatus.employee_id == user_object.employee_id,
            EmployeeStatus.status_id == status_otkomandirovan_id,
            EmployeeStatus.start_date <= python_date.today(),
            (EmployeeStatus.end_date == None) | (EmployeeStatus.end_date >= python_date.today())
        )
    )
    if user_status_record_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action not allowed: User (Manager) is currently seconded out ('Откомандирован').")

    # Check target employee
    target_employee_result = await db.execute(select(Employee).where(Employee.id == target_employee_id))
    target_employee = target_employee_result.scalar_one_or_none()
    if not target_employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target employee not found.")

    if target_employee.division_id != user_s_management_division.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action only allowed for employees within your own management ('Управление').")

    return token_data # Allow if all checks pass

# Helper function for standard Role 3 checks (Manager of Directorate, not seconded out)
async def _perform_standard_role3_checks(token_data: TokenData, db: AsyncSession) -> Division:
    if not token_data.division_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not assigned to any management division.")

    user_s_management_division_result = await db.execute(select(Division).where(Division.id == token_data.division_id))
    user_s_management_division = user_s_management_division_result.scalar_one_or_none()

    if not user_s_management_division or user_s_management_division.division_type != DivisionTypeEnum.DIRECTORATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a manager of a 'Управление' (Directorate).")

    user_object_result = await db.execute(select(User).where(User.id == token_data.user_id))
    user_object = user_object_result.scalar_one_or_none()
    if not user_object or not user_object.employee_id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User's employee record not found for status check.")

    status_otk_result = await db.execute(select(Status.id).filter(Status.code == "SECONDED_OUT"))
    status_otkomandirovan_id = status_otk_result.scalar_one_or_none()
    if not status_otkomandirovan_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server configuration error: 'SECONDED_OUT' status code definition not found.")

    user_status_record_result = await db.execute(
        select(EmployeeStatus).where(
            EmployeeStatus.employee_id == user_object.employee_id,
            EmployeeStatus.status_id == status_otkomandirovan_id,
            EmployeeStatus.start_date <= python_date.today(),
            (EmployeeStatus.end_date == None) | (EmployeeStatus.end_date >= python_date.today())
        )
    )
    if user_status_record_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action not allowed: User (Manager) is currently seconded out ('Откомандирован').")

    return user_s_management_division


from schemas.employee_status import BulkStatusUpdateRequestSchema # For type hint
from models.secondment import SecondmentLog # For type hint
# Assuming SecondmentInitiatePayload is defined in api.v1.secondment or schemas.secondment
# For now, let's assume it's in schemas.secondment if not defined in api/v1/secondment.py directly
# from schemas.secondment import SecondmentInitiatePayload
# If it's in api/v1/secondment.py, this import won't work here directly,
# the endpoint definition will have the type hint. The dependency can take 'payload: BaseModel' or 'payload: Any'
# For better type safety, it should be imported if possible or defined in schemas.
from pydantic import BaseModel # Fallback for payload typing if specific schema not importable here.

class SecondmentInitiatePayloadForDep(BaseModel): # Temporary placeholder if schema not in schemas
    employee_id: int
    target_division_id: int
    start_date: python_date # Using python_date to avoid conflict
    expected_end_date: Optional[python_date] = None


async def check_bulk_status_update_permissions(
    payload: BulkStatusUpdateRequestSchema,
    token_data: TokenData = Depends(get_current_token_data),
    db: AsyncSession = Depends(get_db)
):
    if token_data.role == 4: return token_data
    if token_data.role != 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions for bulk status update.")

    user_s_management_division = await _perform_standard_role3_checks(token_data, db)

    for item in payload.items:
        employee_result = await db.execute(select(Employee).where(Employee.id == item.employee_id))
        employee = employee_result.scalar_one_or_none()
        if not employee or employee.division_id != user_s_management_division.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Cannot update status for employee ID {item.employee_id} outside your management.")
    return token_data

async def check_initiate_secondment_permissions(
    payload: SecondmentInitiatePayloadForDep, # Using placeholder, actual schema from endpoint
    token_data: TokenData = Depends(get_current_token_data),
    db: AsyncSession = Depends(get_db)
):
    if token_data.role == 4: return token_data
    if token_data.role != 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to initiate secondment.")

    user_s_management_division = await _perform_standard_role3_checks(token_data, db)

    employee_result = await db.execute(select(Employee).where(Employee.id == payload.employee_id))
    employee_to_second = employee_result.scalar_one_or_none()
    if not employee_to_second or employee_to_second.division_id != user_s_management_division.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot initiate secondment for an employee outside your management.")
    return token_data

async def check_request_return_permissions(
    secondment_id: int = FastApiPath(..., title="The ID of the secondment log"),
    token_data: TokenData = Depends(get_current_token_data),
    db: AsyncSession = Depends(get_db)
):
    if token_data.role == 4: return token_data

    secondment_log_result = await db.execute(select(SecondmentLog).where(SecondmentLog.id == secondment_id))
    secondment_log = secondment_log_result.scalar_one_or_none()
    if not secondment_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secondment record not found.")

    if token_data.role != 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to request secondment return.")

    user_s_management_division = await _perform_standard_role3_checks(token_data, db) # Standard checks on user

    if secondment_log.original_division_id != user_s_management_division.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only request return for secondments originating from your management.")
    return token_data

async def check_approve_return_permissions(
    secondment_id: int = FastApiPath(..., title="The ID of the secondment log"),
    token_data: TokenData = Depends(get_current_token_data),
    db: AsyncSession = Depends(get_db)
):
    if token_data.role == 4: return token_data

    secondment_log_result = await db.execute(select(SecondmentLog).where(SecondmentLog.id == secondment_id))
    secondment_log = secondment_log_result.scalar_one_or_none()
    if not secondment_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secondment record not found.")

    if token_data.role != 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to approve secondment return.")

    user_s_management_division = await _perform_standard_role3_checks(token_data, db) # Standard checks on user

    if secondment_log.target_division_id != user_s_management_division.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only approve return for secondments targeting your management.")
    return token_data


# Dependency for Role 3 creating an employee in their own management
from schemas.employee import EmployeeCreate # Import schema for request body type hint

async def check_role3_create_in_self_management(
    payload: EmployeeCreate, # FastAPI will pass the request body here
    token_data: TokenData = Depends(get_current_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency to check if a Role 3 user (Management Head) can create an employee.
    Permissions:
    - Role 4 (Admin) can always create (this check is simpler if combined with require_role or handled in endpoint).
      This specific checker focuses on Role 3. If Role 4 should bypass, it should be handled
      either by adding Role 4 to this checker's bypass, or by using a combination of dependencies
      in the endpoint (e.g. `Depends(require_role([3,4]))` then this if role is 3).
      For simplicity here, this checker will pass Role 4.
    - Role 3 can create if:
        - They are a manager of a 'Управление' (Directorate).
        - They are not currently 'Откомандирован' (SECONDED_OUT).
        - The new employee's `division_id` is the manager's own 'Управление' ID.
    """
    if token_data.role == 4: # Admin has full access to create
        return token_data

    if token_data.role != 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Role 3 required for this specific creation.")

    if not token_data.division_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not assigned to any management division.")

    user_s_management_division_result = await db.execute(select(Division).where(Division.id == token_data.division_id))
    user_s_management_division = user_s_management_division_result.scalar_one_or_none()

    if not user_s_management_division or user_s_management_division.division_type != DivisionTypeEnum.DIRECTORATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a manager of a 'Управление' (Directorate).")

    # Check if Role 3 user is "Откомандирован"
    user_object_result = await db.execute(select(User).where(User.id == token_data.user_id))
    user_object = user_object_result.scalar_one_or_none()
    if not user_object or not user_object.employee_id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User's employee record not found for status check.")

    status_otk_result = await db.execute(select(Status.id).filter(Status.code == "SECONDED_OUT"))
    status_otkomandirovan_id = status_otk_result.scalar_one_or_none()
    if not status_otkomandirovan_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server configuration error: 'SECONDED_OUT' status code definition not found.")

    user_status_record_result = await db.execute(
        select(EmployeeStatus).where(
            EmployeeStatus.employee_id == user_object.employee_id,
            EmployeeStatus.status_id == status_otkomandirovan_id,
            EmployeeStatus.start_date <= python_date.today(),
            (EmployeeStatus.end_date == None) | (EmployeeStatus.end_date >= python_date.today())
        )
    )
    if user_status_record_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action not allowed: User (Manager) is currently seconded out ('Откомандирован').")

    # Check if the new employee's division_id matches the manager's division_id
    if payload.division_id != user_s_management_division.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Creation only allowed for employees within your own management ('Управление').")

    return token_data # Allow if all checks pass
