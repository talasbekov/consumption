from datetime import date, timedelta # Added timedelta
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from models import (
    Employee,
    Division,
    Status,
    EmployeeStatus,
    SecondmentLog,
    SecondmentStatusEnum,
    User
)
from schemas.secondment import (
    SecondmentLogCreate, # This might need adjustment based on how original_division_id is handled
    SecondmentLogRead
)
from schemas.employee_status import EmployeeStatusCreate
# Assuming employee_service will be correctly imported from services package
# from services import employee_service # This will be handled in __init__.py later

# Placeholder for the actual employee_service until __init__ is set up
# This is a common pattern: define an interface or import later to avoid circular deps
class EmployeeServicePlaceholder:
    def assign_employee_status(self, db: Session, data: EmployeeStatusCreate) -> EmployeeStatus:
        # This is a placeholder, actual implementation will be used
        raise NotImplementedError("EmployeeService not fully initialized for circular dependency resolution")

employee_service = EmployeeServicePlaceholder()
# This will be replaced by the actual instance from services/__init__.py once everything is set up.
# For now, this allows type checking and method definition.


class SecondmentService:
    def initiate_secondment(
        self,
        db: Session,
        employee_id: int,
        target_division_id: int,
        start_date: date,
        expected_end_date: Optional[date],
        initiating_user_id: Optional[int]
    ) -> SecondmentLogRead:

        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail=f"Employee with id {employee_id} not found")

        if not employee.division_id:
             raise HTTPException(status_code=400, detail=f"Employee with id {employee_id} does not have an assigned division.")

        # Check for existing active secondment
        existing_active_secondment = db.query(SecondmentLog).filter(
            SecondmentLog.employee_id == employee_id,
            SecondmentLog.status == SecondmentStatusEnum.ACTIVE
        ).first()
        if existing_active_secondment:
            raise HTTPException(status_code=400, detail=f"Employee with id {employee_id} already has an active secondment.")

        original_division_id = employee.division_id

        # Fetch "Откомандирован" Status type
        status_seconded_out = db.query(Status).filter(Status.code == 'SECONDED_OUT').first()
        if not status_seconded_out:
            # This should be a configuration error, so 500 is appropriate
            raise HTTPException(status_code=500, detail="Status code 'SECONDED_OUT' not found. Please seed statuses.")

        # Use employee_service to assign the 'Откомандирован' status
        # Note: employee_service.assign_employee_status returns EmployeeStatusRead, but we need EmployeeStatus for internal use or just call it.
        # The actual assign_employee_status in employee_service.py creates an EmployeeStatus record.
        employee_service.assign_employee_status(
            db,
            data=EmployeeStatusCreate(
                employee_id=employee_id,
                status_id=status_seconded_out.id,
                start_date=start_date,
                end_date=expected_end_date,
                note='Откомандирован'
            )
        )

        # Create SecondmentLog instance
        new_secondment_log = SecondmentLog(
            employee_id=employee_id,
            original_division_id=original_division_id,
            target_division_id=target_division_id,
            secondment_start_date=start_date,
            expected_end_date=expected_end_date,
            status=SecondmentStatusEnum.ACTIVE,
            initiating_user_id=initiating_user_id
        )

        db.add(new_secondment_log)
        db.commit()
        db.refresh(new_secondment_log)

        return SecondmentLogRead.from_orm(new_secondment_log)

    def request_secondment_return(
        self,
        db: Session,
        secondment_log_id: int,
        requesting_user_id: Optional[int] # In a real app, this might be mandatory and come from auth
    ) -> SecondmentLogRead:

        secondment_log = db.query(SecondmentLog).filter(SecondmentLog.id == secondment_log_id).first()
        if not secondment_log:
            raise HTTPException(status_code=404, detail=f"SecondmentLog with id {secondment_log_id} not found.")

        if secondment_log.status != SecondmentStatusEnum.ACTIVE:
            raise HTTPException(status_code=400, detail=f"Secondment return can only be requested for 'ACTIVE' secondments. Current status: {secondment_log.status.value}")

        secondment_log.status = SecondmentStatusEnum.RETURN_REQUESTED
        # If you add an 'updated_by_user_id' to SecondmentLog, set it here:
        # secondment_log.updated_by_user_id = requesting_user_id

        db.commit()
        db.refresh(secondment_log)

        return SecondmentLogRead.from_orm(secondment_log) # Corrected typo: SecondLogRead -> SecondmentLogRead

    def approve_secondment_return(
        self,
        db: Session,
        secondment_log_id: int,
        approving_user_id: Optional[int] # In a real app, this might be mandatory
    ) -> SecondmentLogRead:

        secondment_log = db.query(SecondmentLog).filter(SecondmentLog.id == secondment_log_id).first()
        if not secondment_log:
            raise HTTPException(status_code=404, detail=f"SecondmentLog with id {secondment_log_id} not found.")

        if secondment_log.status != SecondmentStatusEnum.RETURN_REQUESTED:
            raise HTTPException(status_code=400, detail=f"Secondment return can only be approved for 'RETURN_REQUESTED' secondments. Current status: {secondment_log.status.value}")

        actual_return_date = date.today()
        secondment_log.status = SecondmentStatusEnum.ENDED
        secondment_log.actual_end_date = actual_return_date
        secondment_log.approving_user_id = approving_user_id

        # Fetch "В строю" Status type
        status_in_service = db.query(Status).filter(Status.code == 'IN_SERVICE').first()
        if not status_in_service:
            raise HTTPException(status_code=500, detail="Status code 'IN_SERVICE' not found. Please seed statuses.")

        # End the previous 'Откомандирован' EmployeeStatus
        # This assumes the 'Откомандирован' status was set with the same start_date as the secondment.
        # And that there's only one such active status. More robust logic might be needed for complex cases.
        active_seconded_out_status = db.query(EmployeeStatus).filter(
            EmployeeStatus.employee_id == secondment_log.employee_id,
            EmployeeStatus.status.has(Status.code == 'SECONDED_OUT'), # Filter by status code
            EmployeeStatus.end_date == secondment_log.expected_end_date # Match based on expected_end_date if set
            # Or, if expected_end_date could be None, match by start_date or lack of end_date
            # EmployeeStatus.start_date == secondment_log.secondment_start_date
        ).order_by(EmployeeStatus.start_date.desc()).first() # Get the latest one

        if active_seconded_out_status:
            # End date should be the day before the actual return, or the return date itself if preferred.
            # Using actual_return_date for simplicity here, meaning the "SECONDED_OUT" status ends when "IN_SERVICE" begins.
            # A common practice is to make the old status end the day before the new one begins.
            active_seconded_out_status.end_date = actual_return_date - timedelta(days=1) if actual_return_date > secondment_log.secondment_start_date else actual_return_date


        # Use employee_service to assign the 'В строю' status
        employee_service.assign_employee_status(
            db,
            data=EmployeeStatusCreate(
                employee_id=secondment_log.employee_id,
                status_id=status_in_service.id,
                start_date=actual_return_date,
                note='Возвращен из командировки'
            )
        )

        # Update employee's division_id back to original_division_id
        employee = db.query(Employee).filter(Employee.id == secondment_log.employee_id).first()
        if employee:
            employee.division_id = secondment_log.original_division_id
        else:
            # This should ideally not happen if foreign keys are enforced
            # and employee existed at the start of secondment.
            # Log this inconsistency.
            pass


        db.commit()
        db.refresh(secondment_log)
        if employee: # also refresh employee if changed
            db.refresh(employee)

        return SecondmentLogRead.from_orm(secondment_log)

# The actual employee_service instance will be injected/set up in services/__init__.py
# For now, the placeholder is used.
# To make this cleaner, one might pass employee_service as a dependency to SecondmentService constructor
# or as a method argument where needed.
# Example: def __init__(self, employee_service_instance): self.employee_service = employee_service_instance
# For this task, global import from services.__init__ is assumed post-setup.
