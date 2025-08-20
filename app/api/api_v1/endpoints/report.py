import datetime
import os
import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    BackgroundTasks,
)
from pydantic import UUID4

from api import deps
from core import settings
from schemas import PDF
from utils import decode_jwt_token
from utils.animals_report import process_animal_data
from utils.farm_calendar_report import process_farm_calendar_data
from utils.irrigation_report import process_irrigation_data
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/{report_id}", response_class=FileResponse)
def retrieve_generated_pdf(
    report_id: str,
    token=Depends(deps.get_current_user),
):
    """

    Retrieve generated PDF file

    """
    user_id = (
        decode_jwt_token(token)["user_id"]
        if settings.REPORTING_USING_GATEKEEPER
        else token.id
    )

    file_path = f"{settings.PDF_DIRECTORY}{user_id}/{report_id}.pdf"

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"File with uuid {report_id} for logged user not found.",
        )

    return FileResponse(
        path=file_path, media_type="application/pdf", filename=f"{report_id}"
    )


@router.post("/irrigation-report/", response_model=PDF)
async def generate_irrigation_report(
    background_tasks: BackgroundTasks,
    token=Depends(deps.get_current_user),
    data: UploadFile = None,
        from_date: datetime.date = None,
        to_date: datetime.date = None
):
    """
    Generates Irrigation Report PDF file

    """
    uuid_v4 = str(uuid.uuid4())
    user_id = (
        decode_jwt_token(token)["user_id"]
        if settings.REPORTING_USING_GATEKEEPER
        else token.id
    )
    uuid_of_pdf = f"{user_id}/{uuid_v4}"

    if not data and not settings.REPORTING_USING_GATEKEEPER:
        raise HTTPException(
            status_code=400,
            detail=f"Data file must be provided if gatekeeper is not used.",
        )

    background_tasks.add_task(
        process_irrigation_data,
        data=data,
        token=token,
        pdf_file_name=uuid_of_pdf,
    from_date=from_date,
    to_date=to_date
    )

    return PDF(uuid=uuid_v4)


@router.post("/compost-report/", response_model=PDF)
async def generate_generic_observation_report(
    background_tasks: BackgroundTasks,
    observation_type_name: str = None,
    token=Depends(deps.get_current_user),
    data: UploadFile = None,
    operation_id: str = None,
    from_date: datetime.date = None,
    to_date: datetime.date = None
):
    """
    Generates Observation Report PDF file
    All Farm Calendar Observation Type values are possible as input

    """

    uuid_v4 = str(uuid.uuid4())
    user_id = (
        decode_jwt_token(token)["user_id"]
        if settings.REPORTING_USING_GATEKEEPER
        else token.id
    )
    uuid_of_pdf = f"{user_id}/{uuid_v4}"

    background_tasks.add_task(
        process_farm_calendar_data,
        observation_type_name=observation_type_name,
        token=token,
        data=data,
        pdf_file_name=uuid_of_pdf,
        operation_id=operation_id,
        from_date=from_date,
        to_date=to_date,
    )

    return PDF(uuid=uuid_v4)


@router.post("/animal-report/", response_model=PDF)
async def generate_animal_report(
    background_tasks: BackgroundTasks,
    token=Depends(deps.get_current_user),
    animal_group: Optional[str] = None,
    name: Optional[str] = None,
    parcel: Optional[UUID4] = None,
    status: Optional[int] = None,
    data: UploadFile = None,
        from_date: datetime.date = None,
        to_date: datetime.date = None
):
    """
    Generates Animal Report PDF file
    """
    uuid_v4 = str(uuid.uuid4())
    user_id = (
        decode_jwt_token(token)["user_id"]
        if settings.REPORTING_USING_GATEKEEPER
        else token.id
    )
    uuid_of_pdf = f"{user_id}/{uuid_v4}"
    params = None
    if not data:
        if not settings.REPORTING_USING_GATEKEEPER:
            raise HTTPException(
                status_code=400,
                detail=f"Data file must be provided if gatekeeper is not used.",
            )

        params = {"format": "json"}
        if animal_group:
            params["animal_group"] = animal_group
        if name:
            params["name"] = name
        if parcel:
            params["parcel"] = str(parcel)
        if status is not None:
            params["status"] = status

    background_tasks.add_task(
        process_animal_data,
        data=data,
        token=token,
        params=params,
        pdf_file_name=uuid_of_pdf,
    from_date=from_date,
    to_date=to_date
    )

    return PDF(uuid=uuid_v4)
