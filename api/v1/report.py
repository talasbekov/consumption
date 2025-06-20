from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import io # For BytesIO for StreamingResponse

from core import get_db
from services import report_service # Assuming report_service is in services.__init__
from schemas.auth import TokenData
from api.v1.auth import get_current_token_data

class ReportRequestPayload(BaseModel):
    division_id: int
    date_from: date
    date_to: Optional[date] = None

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(HTTPBearer())]
)

@router.post(
    "/generate-doc",
    summary="Generate and download DOCX report",
    # response_class=StreamingResponse, # Not needed here, actual response is returned
)
def generate_doc_endpoint(
    payload: ReportRequestPayload,
    db: Session = Depends(get_db),
    token_data: TokenData = Depends(get_current_token_data) # For user info, permissions, audit
):
    # The "завтрашнюю дату по умолчанию" logic mentioned in prompt:
    # If payload.date_from is today, and no date_to, should it be for tomorrow?
    # Current implementation strictly uses payload.date_from.
    # If specific "tomorrow" logic is needed, it would be:
    # if payload.date_from == date.today() and payload.date_to is None:
    #     report_target_date = date.today() + timedelta(days=1)
    # else:
    #     report_target_date = payload.date_from
    # For now, using date_from directly as per Pydantic model.

    report_target_date = payload.date_from
    for_period = payload.date_to is not None and payload.date_to >= payload.date_from

    try:
        file_buffer = report_service.create_word_report_from_template(
            db=db,
            division_id=payload.division_id,
            report_date=report_target_date, # This is the start_date for period logic
            for_period=for_period,
            date_to=payload.date_to
        )
    except FileNotFoundError as e: # If template.docx was to be loaded and not found
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating report: {str(e)}")


    filename = f"report_{payload.division_id}_{report_target_date.strftime('%Y-%m-%d')}.docx"
    if for_period and payload.date_to:
        filename = f"report_{payload.division_id}_{report_target_date.strftime('%Y-%m-%d')}_to_{payload.date_to.strftime('%Y-%m-%d')}.docx"

    return StreamingResponse(
        file_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""} # Ensure filename is quoted
    )
