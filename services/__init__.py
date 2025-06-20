from .rank import rank_service
from .position import position_service
# from .status import status_service # status_service might be removed if not used elsewhere, or kept if it has other utilities
from .division import division_service
from .user import user_service
# Note: status_service was related to the Status model. If ReportService or other services need direct Status model utilities,
# it might be refactored or its functionalities moved. For now, assuming it might not be needed directly if
# ReportService handles its own status lookups. If it IS used by other services, it should remain.
# For this subtask, we are primarily concerned with removing state_service and adding report_service.
from .status import status_service # Keeping status_service for now, assuming it might be used elsewhere.
from .employee import employee_service # employee_service is defined here
from .auth import authenticate_user, create_access_token, get_current_user, get_user_by_email, get_password_hash
from .secondment_service import SecondmentService
from .report_service import ReportService # Import the new ReportService

secondment_service = SecondmentService()
report_service = ReportService() # Instantiate ReportService

# Now, to resolve the placeholder in secondment_service.py:
# One common way is to set it directly after instantiation if the instance is globally available.
# This assumes secondment_service.py's employee_service is a module-level variable.
from . import secondment_service as secondment_service_module
secondment_service_module.employee_service = employee_service
# Alternatively, if SecondmentService took employee_service in __init__, it would be:
# secondment_service = SecondmentService(employee_service=employee_service)
# ReportService does not have cross-service dependencies defined in this step, so no injection needed for it yet.
