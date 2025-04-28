import json
import os
import uuid
from json import JSONDecodeError
from typing import Optional

from fastapi import (
    APIRouter,
    File,
    Depends,
    HTTPException,
    UploadFile,
    Response,
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
from utils.json_handler import make_get_request
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("{report_id}", response_class=FileResponse)
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

    if not data:
        params = {"format": "json"}
        farm_calendar_irrigation_response = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["irrigations"]}',
            token=token,
            params=params,
        )

        if not farm_calendar_irrigation_response:
            raise HTTPException(status_code=400, detail="No Irrigation data found.")

        background_tasks.add_task(
            process_irrigation_data,
            json_data=farm_calendar_irrigation_response,
            pdf_file_name=uuid_of_pdf,
        )

        return PDF(uuid=uuid_v4)

    else:
        try:
            background_tasks.add_task(
                process_irrigation_data,
                json_data=json.load(data.file),
                pdf_file_name=uuid_of_pdf,
            )

            return PDF(uuid=uuid_v4)

        except JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Reporting service failed during PDF generation. File is not correct JSON.",
            )


@router.post("/compost-report/", response_model=PDF)
async def generate_generic_observation_report(
    observation_type_name: str,
    background_tasks: BackgroundTasks,
    token=Depends(deps.get_current_user),
    data: UploadFile = None,
):
    """
    Generates Observation Report PDF file
    possible_names = ["Pesticides", "Irrigation", "Fertilization", "CropStressIndicator", "CropGrowthObservation"]


    """
    if observation_type_name == "CropGrowthObservation":
        observation_type_name = "Crop Growth Stage Observation"

    if observation_type_name == "CropStressIndicator":
        observation_type_name = "Crop Stress Indicator"
    uuid_v4 = str(uuid.uuid4())
    user_id = (
        decode_jwt_token(token)["user_id"]
        if settings.REPORTING_USING_GATEKEEPER
        else token.id
    )
    uuid_of_pdf = f"{user_id}/{uuid_v4}"

    if not data:
        if not settings.REPORTING_USING_GATEKEEPER:
            raise HTTPException(
                status_code=400,
                detail=f"Data file must be provided if gatekeeper is not used.",
            )

        params = {"format": "json", "name": observation_type_name}
        farm_activity_type_info = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["activity_types"]}',
            token=token,
            params=params,
        )

        if not farm_activity_type_info:
            raise HTTPException(status_code=400, detail="Activity Type API failed.")

        del params["name"]
        params["activity_type"] = farm_activity_type_info[0]["@id"].split(":")[3]

        observations = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["observations"]}',
            token=token,
            params=params,
        )

        if not observations:
            raise HTTPException(status_code=400, detail="Observations are empty.")

        farm_activities = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["activities"]}',
            token=token,
            params=params,
        )

        if not farm_activities:
            raise HTTPException(status_code=400, detail="Farm Activities are empty.")

        background_tasks.add_task(
            process_farm_calendar_data,
            activity_type_info=observation_type_name,
            observations=observations,
            farm_activities=farm_activities,
            pdf_file_name=uuid_of_pdf,
        )

        return PDF(uuid=uuid_v4)
    else:
        try:
            dt = json.load(data.file)

            background_tasks.add_task(
                process_farm_calendar_data,
                activity_type_info=observation_type_name,
                observations=dt["observations"],
                farm_activities=dt["farm_activities"],
                pdf_file_name=uuid_of_pdf,
            )

            return PDF(uuid=uuid_v4)

        except JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Reporting service failed during PDF generation. File is not correct JSON.",
            )


@router.post("/animal-report/", response_model=PDF)
async def generate_animal_report(
    background_tasks: BackgroundTasks,
    token=Depends(deps.get_current_user),
    animal_group: Optional[str] = None,
    name: Optional[str] = None,
    parcel: Optional[UUID4] = None,
    status: Optional[int] = None,
    data: UploadFile = None,
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

        json_response = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["animals"]}',
            token=token,
            params=params,
        )

        if not json_response:
            raise HTTPException(status_code=400, detail="No animal data found.")

        background_tasks.add_task(
            process_animal_data, json_data=json_response, pdf_file_name=uuid_of_pdf
        )

        return PDF(uuid=uuid_v4)

    else:
        try:
            background_tasks.add_task(
                process_animal_data,
                json_data=json.load(data.file),
                pdf_file_name=uuid_of_pdf,
            )

            return PDF(uuid=uuid_v4)

        except JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Reporting service failed during PDF generation. File is not correct JSON.",
            )
