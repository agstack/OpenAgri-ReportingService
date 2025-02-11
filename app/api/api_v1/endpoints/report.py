import json
import uuid
from json import JSONDecodeError
from fastapi import APIRouter, File, Depends, HTTPException, UploadFile, Response
from api import deps
from models import User
from core import settings
from utils.irrigation_report import process_irrigation_data
from utils.json_handler import make_get_request

router = APIRouter()


@router.post("/irrigation-report/")
async def generate_irrigation_report(
    token=Depends(deps.get_current_user),
    data: UploadFile = None,
):
    """
    Generates Irrigation Report PDF file

    """

    pdf = None
    if not data:
        if not settings.REPORTING_USING_GATEKEEPER:
            raise HTTPException(
                status_code=400,
                detail=f"Data file must be provided if gatekeeper is not used.",
            )

        params = {"format": "json"}
        json_response = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["irrigations"]}',
            token=token,
            params=params,
        )

        if not json_response:
            raise HTTPException(status_code=400, detail="No Irrigation data found.")

        pdf = process_irrigation_data(json_data=json_response)

    else:
        try:
            pdf = process_irrigation_data(json_data=json.load(data.file))

        except JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Reporting service failed during PDF generation. File is not correct JSON.",
            )

    if not pdf:
        raise HTTPException(
            status_code=400,
            detail=f"Reporting service failed during PDF generation.",
        )

    headers = {
        "Content-Disposition": "attachment; filename={}-report-{}.pdf".format(
            "irrigation", uuid.uuid4()
        )
    }

    return Response(
        content=bytes(pdf.output()), media_type="application/pdf", headers=headers
    )
