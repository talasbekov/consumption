
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from core import get_db
import logging
from services import data_service

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/random/datas", tags=["Datass"], dependencies=[Depends(HTTPBearer())])


@router.post("/populate_all/", response_model=dict)
def populate_all(db:Session = Depends(get_db)):
    try:
        data_service.create_employers_for_state(db)
        return {"status": "Added records to all tables"}
    except Exception as e:
        logger.error(f"Error populating tables: {e}")
        raise HTTPException(status_code=500, detail="Failed to populate tables due to a server error")


@router.post("/bulk/upload/photos")
async def upload_photos(directory: str, db: Session = Depends(get_db)):
    return await data_service.upload_photos_from_directory(directory, db)

