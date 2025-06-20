from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import date, datetime, timedelta # Added datetime, timedelta
from typing import Optional, List, Dict, Any # Added Any

from fastapi import HTTPException

from models import (
    Employee,
    Division,
    Position, # May not be used if focusing on Employee.division_id
    Status,
    EmployeeStatus,
    SecondmentLog,
    User,
    SecondmentStatusEnum # For seconded-in calculation
)
# from models import State # Explicitly not importing State

# Placeholder for create_word_report_from_template if it's moved or adapted later
# For now, this service will focus on data generation.
# from utils.report_generator import create_word_report_from_template

class ReportService:
    def _format_date(self, date_value: Any) -> str:
        if date_value is None:
            return ""
        elif isinstance(date_value, datetime):
            return date_value.strftime("%d.%m.%Y")
        elif isinstance(date_value, date):
            return date_value.strftime("%d.%m.%Y")
        elif isinstance(date_value, str):
            try:
                parsed_date = datetime.strptime(date_value, "%Y-%m-%d")
                return parsed_date.strftime("%d.%m.%Y")
            except ValueError:
                # Attempt another common format if the first one fails
                try:
                    parsed_date = datetime.strptime(date_value, "%d.%m.%Y")
                    return parsed_date.strftime("%d.%m.%Y") # Or return as is if already in desired format
                except ValueError:
                    # print(f"Ошибка преобразования даты: {date_value}. Неизвестный формат.") # Consider logging
                    return date_value # Return original if all parsing fails
        else:
            # print(f"Неожиданный тип данных для даты: {date_value} ({type(date_value)})") # Consider logging
            return ""

    # Copied from services/state.py and will be adapted
    def get_count_of_state(self, db: Session, user_id: int)-> dict[
        str | Any, dict[str, int | str] | dict[str, int | str] | dict[str, int | str] | dict[
            str, int | str] | dict[str, int | Any]]: # Changed InstrumentedAttribute to Any
        # This method needs significant refactoring to not use self.model and user_id for department context
        # For now, porting as is and will refactor in next step.
        print(user_id)
        # user = user_service.get_by_id(db, user_id) # user_service is not defined here yet
        # print(user.employee_id)
        emps = []
        # states = db.query(self.model).all() # self.model is State, needs to change
        # for state_obj in states: # Renamed state to state_obj to avoid conflict with local var
        #     emps.append(state_obj.employee_id)

        # state = None # This variable 'state' refers to an instance of the old State model.
        index = 0

        # while state is None and index < len(emps):
        #     employee_id = emps[index]
        #     state = db.query(self.model).filter(self.model.employee_id == employee_id).first()
        #     index += 1

        # if state is not None:
        #     print("Found state:", state)
        # else:
        #     print("No valid state found")
        #     # This will cause errors below if state is None, needs guard or proper context
        #     # For now, returning empty or raising error if context cannot be determined
        #     raise HTTPException(status_code=404, detail="Reporting context (e.g., department) could not be determined for the user.")


        # state_count = db.query(self.model).filter(self.model.department_id == state.department_id).count()
        # vacant_count = db.query(self.model).filter(self.model.employee_id.is_(None)).count()
        # by_list_count = state_count - vacant_count
        # inline_count = (
        #     db.query(Employee)
        #     .join(EmployeeStatus, EmployeeStatus.employee_id == Employee.id)
        #     .join(Status, Status.id == EmployeeStatus.status_id)
        #     .join(self.model, self.model.employee_id == Employee.id) # self.model is State
        #     .filter(self.model.department_id == state.department_id)
        #     .filter(Status.nameRU == "в строю") # TODO: Change to Status.code
        #     .count()
        # )
        # by_status_count = by_list_count - inline_count

        # result = {
        #     "by state": {"count": state_count, "name": "по штату"},
        #     "by list": {"count": by_list_count, "name": "по списку"},
        #     "by vacant": {"count": vacant_count, "name": "ваканты"},
        #     "by status": {"count": by_status_count, "name": "общее количество отсутствующих"},
        # }

        # statuses = db.query(Status).all()
        # for status_obj in statuses: # Renamed status to status_obj
        #     count = (
        #         db.query(Employee)
        #         .join(EmployeeStatus, EmployeeStatus.employee_id == Employee.id)
        #         .join(Status, Status.id == EmployeeStatus.status_id)
        #         .join(self.model, self.model.employee_id == Employee.id) # self.model is State
        #         .filter(self.model.department_id == state.department_id)
        #         .filter(Status.nameRU == status_obj.nameRU) # TODO: Change to Status.code
        #         .count()
        #     )
        #     result[status_obj.nameEN] = {"count": count, "name": status_obj.nameRU}
        # return result
        raise NotImplementedError("get_count_of_state needs to be refactored.")


    # Copied from services/state.py and will be adapted
    def generate_division_report_data(self, db: Session, division_id: int, report_date: date) -> Dict[str, Any]:
        # user_id is replaced by division_id and report_date
        # The old logic relied on user's state to find department and then managements.
        # New logic: division_id is the top-level division for the report.
        # Iterate its sub-divisions (e.g., managements if division_id is a department, or offices if it's a management).

        report_data: Dict[str, Any] = {}

        # Fetch the main division for the report
        main_division = db.query(Division).filter(Division.id == division_id).first()
        if not main_division:
            raise HTTPException(status_code=404, detail=f"Division with id {division_id} not found.")

        # Determine sub-divisions to iterate over based on main_division's type or structure
        # This is a placeholder for actual hierarchy logic.
        # Example: if main_division is a Department, sub_divisions could be its Managements.
        # If it's a Management, sub_divisions could be its Offices/Units.
        # For now, let's assume we report on the division_id itself and its direct children as an example.

        sub_divisions_to_report = [main_division] # Start with the main division
        # Add logic to find children divisions if necessary:
        # children_divisions = db.query(Division).filter(Division.parent_division_id == main_division.id).all()
        # sub_divisions_to_report.extend(children_divisions)

        # Fetch all Status types once
        statuses_db = db.query(Status).all()
        # Create a dictionary for quick lookup by code, if preferred, or by ID.
        # Using nameEN as key as in old code, but ideally should be status.code
        statuses_info_dict: Dict[str, Dict[str, Any]] = {
            status.nameEN: {"id": status.id, "nameRU": status.nameRU, "code": status.code} for status in statuses_db
        }
        # Or by status.id if iterating through employees' statuses
        # status_details_by_id: Dict[int, Dict[str, Any]] = {
        #    s.id: {"nameRU": s.nameRU, "nameEN": s.nameEN, "code": s.code} for s in statuses_db
        # }


        # --- Refactoring "Басшылық" (Leadership/Top-level division part of the old report) ---
        # This part of the old code calculated stats for the department itself, excluding sub-managements.
        # We will adapt this for the current 'd' (a sub_division_to_report)

        for current_report_division in sub_divisions_to_report:
            division_stats: Dict[str, Any] = {}

            # Штат (Staff count) - This is complex without a dedicated "slots" table.
            # Old: state_count = db.query(func.count(self.model.id)).filter(...)
            # New: Placeholder - How is "штат" defined for a division? If it's just current employees, it's "по списку".
            # If there's a Division.staff_count field, use that.
            # For now, let's assume staff_count might be a property of the division or calculated.
            # This needs clarification based on actual business logic for "штат".
            staff_count = 0 # Placeholder for "по штату"

            # Список (By List - actual employees in division)
            employees_in_division = db.query(Employee).filter(Employee.division_id == current_report_division.id).all()
            by_list_count = len(employees_in_division)
            division_stats["by state"] = {"count": staff_count, "name": "по штату"} # Placeholder for staff_count
            division_stats["by list"] = {"count": by_list_count, "name": "по списку"}

            # Вакантные (Vacant) = Штат - Список (if "Штат" is defined)
            vacant_count = staff_count - by_list_count if staff_count > by_list_count else 0 # Placeholder
            division_stats["by vacant"] = {"count": vacant_count, "name": "ваканты"}

            # Collect employee details for each status
            all_status_details_for_division: Dict[str, List[Dict[str, Any]]] = {
                 s_info["nameEN"]: [] for s_code, s_info in statuses_info_dict.items()
            }

            # Counts for each status
            status_counts_in_division: Dict[str, int] = {
                s_info["nameEN"]: 0 for s_code, s_info in statuses_info_dict.items()
            }

            for emp in employees_in_division:
                # Find current status for 'report_date'
                current_employee_status_record = db.query(EmployeeStatus)\
                    .join(Status)\
                    .filter(EmployeeStatus.employee_id == emp.id)\
                    .filter(EmployeeStatus.start_date <= report_date)\
                    .filter((EmployeeStatus.end_date == None) | (EmployeeStatus.end_date >= report_date))\
                    .order_by(EmployeeStatus.start_date.desc(), EmployeeStatus.id.desc())\
                    .first()

                if current_employee_status_record:
                    status_details = db.query(Status).filter(Status.id == current_employee_status_record.status_id).first()
                    if status_details and status_details.nameEN in status_counts_in_division: # nameEN used as key in old code
                        status_counts_in_division[status_details.nameEN] += 1

                        # Prepare employee detail for the report (FIO, status period, note)
                        employee_info_for_status = {
                            "ФИО": f"{emp.surname} {emp.firstname[0].upper() if emp.firstname else ''}.", # Assuming emp has surname & firstname
                            "Статус": status_details.nameRU,
                            "Дата начало": self._format_date(current_employee_status_record.start_date),
                            "Дата окончание": self._format_date(current_employee_status_record.end_date),
                            "Примечание": current_employee_status_record.note
                        }
                        all_status_details_for_division[status_details.nameEN].append(employee_info_for_status)

            # Populate division_stats with counts and employee details for each status
            for s_name_en, s_info_dict in statuses_info_dict.items():
                s_name_ru = s_info_dict["nameRU"]
                division_stats[s_name_en] = {
                    "count": status_counts_in_division.get(s_name_en, 0),
                    "name": f"{s_name_ru} ({s_name_en})", # Original format
                    f"сотрудники со статусом {s_name_ru}": all_status_details_for_division.get(s_name_en, [])
                }

            # "В строю" (In Service) count - specific calculation often highlighted
            # Assuming 'IN_SERVICE' is the code for "в строю"
            in_service_status_info = next((s for s in statuses_db if s.code == 'IN_SERVICE'), None)
            if in_service_status_info:
                 # This count is already in division_stats[in_service_status_info.nameEN]['count']
                 # The old code had a separate 'inline_count', which seems to be "в строю".
                 # If "inline" means something else, this needs clarification.
                 # For now, "в строю" is just one of the statuses.
                 pass


            # Прикомандированные (Seconded-In to this division)
            seconded_in_employees = db.query(SecondmentLog)\
                .filter(SecondmentLog.target_division_id == current_report_division.id)\
                .filter(SecondmentLog.status == SecondmentStatusEnum.ACTIVE)\
                .filter(SecondmentLog.secondment_start_date <= report_date)\
                .filter((SecondmentLog.actual_end_date == None) | (SecondmentLog.actual_end_date > report_date))\
                .all()
            # Add details for seconded-in if needed in the report under a specific key
            division_stats["seconded_in"] = { # Or use the Russian name/EN code from Status table if "Прикомандирован" is a status
                "count": len(seconded_in_employees),
                "name": "Прикомандированные (+)", # Or lookup from Status table
                # Optionally list FIOs etc.
            }

            # Откомандированные (Seconded-Out from this division)
            # This is typically one of the statuses counted above if "Откомандирован" is a status type.
            # If 'SECONDED_OUT' is the code:
            seconded_out_status_info = next((s for s in statuses_db if s.code == 'SECONDED_OUT'), None)
            if seconded_out_status_info:
                # This count is already in division_stats[seconded_out_status_info.nameEN]['count']
                pass


            report_data[current_report_division.nameRU if current_report_division.nameRU else f"Division_{current_report_division.id}"] = division_stats

        # --- Refactoring "Барлығы" (Totals) ---
        # The old code called self.get_count_of_state for totals.
        # This needs to be a new calculation based on the sum of main_division and its children,
        # or a separate query if the definition of "total" is different.
        # For now, this part is complex and depends on precise definition of "total".
        # Placeholder for total calculation logic:
        # report_data["Барлығы"] = self._calculate_overall_totals(db, main_division, report_date, statuses_db)

        return report_data
        # raise NotImplementedError("generate_division_report_data is partially refactored. Focus on hierarchy and status counts.")


    def _calculate_overall_totals(self, db: Session, main_division: Division, report_date: date, statuses_db: List[Status]) -> Dict[str, Any]:
        # This method would sum up the counts from the main_division and its relevant sub-divisions
        # that were included in the report_data.
        # Or, it might perform new queries over the entire scope defined by main_division.
        # For now, returning a placeholder.
        return {"message": "Total calculation logic not yet implemented."}


# This instantiation will be done in services/__init__.py as per instructions
