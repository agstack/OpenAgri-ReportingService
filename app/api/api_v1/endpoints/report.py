import datetime
import os
import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    BackgroundTasks,
)
from pydantic import UUID4

from api import deps
from core import settings
from schemas import PDF, ManualFarmInfo, ManualParcelInfo
from utils import decode_jwt_token
from utils.animals_report import process_animal_data
from utils.farm_calendar_report import process_farm_calendar_data
from utils.irrig_fert_pest_report import process_irrigation_fertilization_data
from utils.standalone_observation_report import process_standalone_observation_data
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/{report_id}/", response_class=FileResponse)
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
            status_code=202,
            detail=f"PDF uuid {report_id} is being generated. Please be patient and try again in couple of seconds.",
        )

    return FileResponse(
        path=file_path, media_type="application/pdf", filename=f"{report_id}"
    )


@router.post("/irrigation-report/", response_model=PDF)
async def generate_irrigation_report(
    background_tasks: BackgroundTasks,
    token=Depends(deps.get_current_user),
    irrigation_id: str = None,
    data: UploadFile = None,
    from_date: datetime.date = None,
    to_date: datetime.date = None,
    parcel_id: str = None
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
    if data:
        data = data.file.read()
    background_tasks.add_task(
        process_irrigation_fertilization_data,
        data=data,
        token=token,
        pdf_file_name=uuid_of_pdf,
        from_date=from_date,
        to_date=to_date,
        operation_id=irrigation_id,
        parcel_id=parcel_id
    )

    return PDF(uuid=uuid_v4)


@router.post("/compost-report/", response_model=PDF)
async def generate_generic_observation_report(
    background_tasks: BackgroundTasks,
    calendar_activity_type: str = None,
    token=Depends(deps.get_current_user),
    data: UploadFile = None,
    operation_id: str = None,
    from_date: datetime.date = None,
    to_date: datetime.date = None,
    parcel_id: str = None
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
    if data:
        data = data.file.read()
    background_tasks.add_task(
        process_farm_calendar_data,
        calendar_activity_type=calendar_activity_type,
        token=token,
        data=data,
        pdf_file_name=uuid_of_pdf,
        operation_id=operation_id,
        from_date=from_date,
        to_date=to_date,
        parcel_id=parcel_id
    )

    return PDF(uuid=uuid_v4)


@router.post("/animal-report/", response_model=PDF)
async def generate_animal_report(
    background_tasks: BackgroundTasks,
    token=Depends(deps.get_current_user),
    farm_animal_id: str = None,
    animal_group: Optional[str] = None,
    name: Optional[str] = None,
    parcel: Optional[UUID4] = None,
    status: Optional[int] = None,
    data: UploadFile = None,
    from_date: datetime.date = None,
    to_date: datetime.date = None,
    parcel_id: str = None
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

        params = {}
        if animal_group:
            params["animal_group"] = animal_group
        if name:
            params["name"] = name
        if parcel:
            params["parcel"] = str(parcel)
        if status is not None:
            params["status"] = status
        if parcel_id:
            params['parcel'] = parcel_id
    if data:
        data = data.file.read()
    background_tasks.add_task(
        process_animal_data,
        data=data,
        token=token,
        params=params,
        pdf_file_name=uuid_of_pdf,
        from_date=from_date,
        to_date=to_date,
        farm_animal_id=farm_animal_id,
    )

    return PDF(uuid=uuid_v4)



@router.post("/fertilization-report/", response_model=PDF)
async def generate_fertilization_report(
    background_tasks: BackgroundTasks,
    token=Depends(deps.get_current_user),
    fertilization_id: str = None,
    data: UploadFile = None,
    from_date: datetime.date = None,
    to_date: datetime.date = None,
    parcel_id: str = None
):
    """
    Generates Fertilization Report PDF file

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
    if data:
        data = data.file.read()
    background_tasks.add_task(
        process_irrigation_fertilization_data,
        data=data,
        token=token,
        pdf_file_name=uuid_of_pdf,
        from_date=from_date,
        to_date=to_date,
        operation_id=fertilization_id,
        parcel_id=parcel_id,
        irrigation_flag=False,
        fertilization_flag=True
    )

    return PDF(uuid=uuid_v4)


@router.get("/standalone-observation-report/{report_id}/", response_class=FileResponse)
def retrieve_standalone_observation_pdf(report_id: str):
    """
    Retrieve a standalone-observation PDF. No authentication required —
    matches the no-auth POST endpoint.
    """
    file_path = f"{settings.PDF_DIRECTORY}standalone/{report_id}.pdf"

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=202,
            detail=f"PDF uuid {report_id} is being generated. Please be patient and try again in couple of seconds.",
        )

    return FileResponse(
        path=file_path, media_type="application/pdf", filename=f"{report_id}"
    )


@router.post("/standalone-observation-report/", response_model=PDF)
async def generate_standalone_observation_report(
    background_tasks: BackgroundTasks,
    data: UploadFile = File(..., description="JSON file containing a pure JSON-LD observation array"),
    title: str = Form("Observation Report"),
    from_date: Optional[datetime.date] = Form(None),
    to_date: Optional[datetime.date] = Form(None),
    parcel_address: str = Form(""),
    parcel_identifier: str = Form(""),
    parcel_area: float = Form(0.0),
    parcel_lat: Optional[float] = Form(None),
    parcel_lng: Optional[float] = Form(None),
    farm_name: str = Form(""),
    farm_municipality: str = Form(""),
    farm_administrator: str = Form(""),
    farm_vat_id: str = Form(""),
    farm_contact_person: str = Form(""),
    farm_description: str = Form(""),
):
    """
    Generates an Observation Report PDF from a pure JSON-LD observation array.

    Unlike the other endpoints, no Farm Calendar lookups happen here and no
    authentication is required. Parcel and farm information must be supplied
    manually as form fields, and the observation data must be uploaded as a
    top-level JSON array (e.g. `[ {"@type": "Observation", ...}, ... ]`).
    """
    uuid_v4 = str(uuid.uuid4())
    uuid_of_pdf = f"standalone/{uuid_v4}"

    parcel = ManualParcelInfo(
        address=parcel_address,
        identifier=parcel_identifier,
        area=parcel_area,
        lat=parcel_lat,
        lng=parcel_lng,
    )
    farm = ManualFarmInfo(
        name=farm_name,
        municipality=farm_municipality,
        administrator=farm_administrator,
        vatID=farm_vat_id,
        contactPerson=farm_contact_person,
        description=farm_description,
    )

    file_bytes = data.file.read()

    background_tasks.add_task(
        process_standalone_observation_data,
        data=file_bytes,
        pdf_file_name=uuid_of_pdf,
        parcel=parcel,
        farm=farm,
        title=title,
        from_date=from_date,
        to_date=to_date,
    )

    return PDF(uuid=uuid_v4)


@router.post("/pesticides-report/", response_model=PDF)
async def generate_pesticides_report(
    background_tasks: BackgroundTasks,
    token=Depends(deps.get_current_user),
    pesticide_id: str = None,
    data: UploadFile = None,
    from_date: datetime.date = None,
    to_date: datetime.date = None,
    parcel_id: str = None
):
    """
    Generates Pesticides Report PDF file

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

    if data:
        data = data.file.read()

    background_tasks.add_task(
        process_irrigation_fertilization_data,
        data=data,
        token=token,
        pdf_file_name=uuid_of_pdf,
        from_date=from_date,
        to_date=to_date,
        operation_id=pesticide_id,
        parcel_id=parcel_id,
        irrigation_flag=False,
        pesticides_flag= True
    )

    return PDF(uuid=uuid_v4)