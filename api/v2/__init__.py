from fastapi import APIRouter

from .auth import router as auth2_router
from .user import router as user2_router
from .department import router as department_router
from .management import router as management_router
from .division import router as division_router
from .employer import router as emp_router
from .state import router as state_router
from .position import router as position_router
from .rank import router as rank_router
from .data_for_employers import router as data_router
from .status import router as status_router


router = APIRouter(prefix="/v2")

router.include_router(auth2_router)
router.include_router(user2_router)
router.include_router(department_router)
router.include_router(management_router)
router.include_router(division_router)
router.include_router(emp_router)
router.include_router(state_router)
router.include_router(position_router)
router.include_router(rank_router)
router.include_router(data_router)
router.include_router(status_router)
