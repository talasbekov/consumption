from fastapi import APIRouter

from .auth import router as auth2_router
from .user import router as user2_router
from .division import router as division_router
from .employee import router as emp_router

from .position import router as position_router
from .rank import router as rank_router
# from .data_for_employees import router as data_router
from .status import router as status_router


router = APIRouter(prefix="/v1")

router.include_router(auth2_router)
router.include_router(user2_router)
router.include_router(division_router)
router.include_router(emp_router)

router.include_router(position_router)
router.include_router(rank_router)
# router.include_router(data_router)
router.include_router(status_router)
