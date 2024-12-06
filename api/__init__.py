from fastapi import APIRouter, Request
from .v1 import router as v2_router


router = APIRouter(prefix="/api")

@v2_router.get("/ip")
async def get_ip(request: Request):
    return request.client.host


router.include_router(v2_router)
