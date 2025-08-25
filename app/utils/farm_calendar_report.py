import datetime
import json
import logging
import os
from typing import Union
from fastapi import HTTPException

from core import settings
from fpdf import FontFace
from fpdf.enums import VAlign
from schemas.compost import *
from utils import EX, add_fonts, decode_dates_filters, get_parcel_info
from utils.json_handler import make_get_request
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="reportin_app")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FarmCalendarData:
    """Class to process and store connected farm calendar data"""

    def __init__(
            self,
            activity_type_info: str,
            observations: Union[dict, str, list],
            farm_activities: Union[dict, str, list],
            materials: Union[dict, str, list],
    ):
        self.activity_type = activity_type_info
        try:
            self.observations = [
                CropObservation.model_validate(obs) for obs in observations
            ]
            self.operations = [Operation.model_validate(act) for act in farm_activities]
            self.materials = [AddRawMaterialOperation.model_validate(mat) for mat in materials]
        except Exception as e:
            logger.error(f"Error parsing farm calendar data: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Reporting service failed during data validation. File is not correct JSON. {e}",
            )


def create_farm_calendar_pdf(calendar_data: FarmCalendarData, token: dict[str, str]) -> EX:
    """Create PDF report from farm calendar data"""
    pdf = EX()
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    EX.ln(pdf)

    pdf.set_font("FreeSerif", "B", 14)
    pdf.cell(0, 10, f"{calendar_data.activity_type} Report", ln=True, align="C")
    pdf.set_font("FreeSerif", style="", size=9)
    pdf.cell(0, 7, f"Farm Calendar Operation Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("FreeSerif", "B", 12)
    pdf.cell(0, 10, "Activity Type Information", ln=True, align="L")
    pdf.set_fill_color(230, 230, 230)

    y_position = pdf.get_y()
    line_end_x = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.line(pdf.l_margin, y_position, line_end_x, y_position)
    pdf.ln(5)

    if len(calendar_data.operations) == 1:
        operation = calendar_data.operations[0]

        agr_mach_id = operation.usesAgriculturalMachinery[0].get("@id", "N/A").split(":")[
            -1] if operation.usesAgriculturalMachinery else None
        if agr_mach_id:
            agr_resp = make_get_request(
                url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["machines"]}{agr_mach_id}/',
                token=token,
                params={"format": "json"}
            )
            if agr_resp:
                parcel_id = agr_resp.get("hasAgriParcel", {}).get("@id", "N/A").split(":")[-1]
                address, farm = get_parcel_info(parcel_id, token, geolocator)

                pdf.set_font("FreeSerif", "B", 10)
                pdf.cell(40, 8, "Parcel Location:")
                pdf.set_font("FreeSerif", "", 10)
                pdf.multi_cell(0, 8, address, ln=True, fill=True)

                pdf.set_font("FreeSerif", "B", 10)
                pdf.cell(40, 8, "Farm information:",)
                pdf.set_font("FreeSerif", "", 10)
                pdf.multi_cell(0, 8, farm, ln=True, fill=True)


        cp_id = operation.isOperatedOn.get("@id", "N/A").split(":")[-1] if operation.isOperatedOn else 'N/A'
        start_date = operation.hasStartDatetime.strftime("%d/%m/%Y") if operation.hasStartDatetime else operation.phenomenonTime
        end_date = operation.hasEndDatetime.strftime("%d/%m/%Y") if operation.hasEndDatetime else "N/A"

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Details:")
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, str(operation.details), ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Starting Date:")
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, str(start_date), ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Ending Date:")
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, str(end_date), ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Compost Pile:")
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, str(cp_id), ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Initial Materials:")
        pdf.ln(15)
        if calendar_data.materials:
            with pdf.table(text_align="CENTER", padding=0.5, v_align=VAlign.M) as table:
                pdf.set_font("FreeSerif", "", 10)
                row = table.row()
                row.cell("Name")
                row.cell("Unit")
                row.cell("Numeric value")
                pdf.set_font("FreeSerif", "", 9)
                row = table.row()
                x = calendar_data.materials[0].hasCompostMaterial[0] if calendar_data.materials[0].hasCompostMaterial else None
                row.cell(x.typeName if x else 'N/A')
                row.cell(x.quantityValue.unit if x.quantityValue else 'N/A')
                row.cell(str(x.quantityValue.numericValue) if x.quantityValue else 'N/A')


    pdf.set_fill_color(0, 255, 255)
    if len(calendar_data.operations) > 1:
        with pdf.table(text_align="CENTER", padding=0.5) as table:

            pdf.set_font("FreeSerif", "B", 12)
            pdf.cell(0, 10, "Operations", ln=True)
            pdf.ln(5)

            row = table.row()
            pdf.set_font("FreeSerif", "B", 10)
            row.cell("Title")
            row.cell("Details")
            row.cell("Start")
            row.cell("End")
            row.cell("Agent")
            row.cell("Machinery IDs")
            row.cell("Parcel")
            row.cell("Farm")
            row.cell("Compost Pile")
            pdf.set_font("FreeSerif", "", 9)
            pdf.set_fill_color(255, 255, 240)
            for operation in calendar_data.operations:
                row = table.row()
                row.cell(operation.title)
                row.cell(operation.details)
                row.cell(
                    f"{operation.hasStartDatetime.strftime('%d/%m/%Y') if operation.hasStartDatetime else 'N/A'}",
                )
                row.cell(
                    f"{operation.hasEndDatetime.strftime('%d/%m/%Y') if operation.hasEndDatetime else 'N/A'} ",
                )
                row.cell(operation.responsibleAgent)
                machinery_ids = ''
                address, farm = '', ''
                if operation.usesAgriculturalMachinery:
                    machinery_ids = ", ".join(
                        [
                            machinery.get("@id", "N/A").split(":")[3]
                            for machinery in operation.usesAgriculturalMachinery
                        ]
                    )
                    agr_mach_id = operation.usesAgriculturalMachinery[0].get("@id", "N/A").split(":")[
                        -1]
                    agr_resp = make_get_request(
                        url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["machines"]}{agr_mach_id}/',
                        token=token,
                        params={"format": "json"}
                    )
                    if agr_resp:
                        parcel_id = agr_resp.get("hasAgriParcel", {}).get("@id", "N/A").split(":")[-1]
                        address, farm = get_parcel_info(parcel_id, token, geolocator)
                row.cell(f"{machinery_ids}")
                row.cell(address)
                row.cell(farm)
                operation = calendar_data.operations[0]
                cp = operation.isOperatedOn.get("@id", "N/A").split(":")[
                    3] if operation.isOperatedOn else 'Empty Pile Value'
                row.cell(cp)

    if calendar_data.observations:
        pdf.ln()
        pdf.set_fill_color(0, 255, 255	)

        pdf.set_font("FreeSerif", "B", 12)
        pdf.cell(0, 10, "Observations", ln=True)
        pdf.ln(5)

        with pdf.table(text_align="CENTER", padding=0.5, v_align=VAlign.M) as table:
            row = table.row()
            pdf.set_font("FreeSerif", "B", 10)
            row.cell("Value info")
            row.cell("Observed Property")
            row.cell("Details")
            row.cell("Start")
            row.cell("End")
            row.cell("Responsible Agent")
            pdf.set_font("FreeSerif", "", 9)
            for x in calendar_data.observations:
                row = table.row()
                pdf.set_fill_color(255, 255, 240)
                (
                    row.cell(f"{x.hasResult.hasValue} ({x.hasResult.unit})")
                    if x.hasResult
                    else row.cell("N/A")
                )
                (
                    row.cell(f"{x.observedProperty}")
                    if x.observedProperty
                    else row.cell("N/A")
                )
                row.cell(f"{x.details}")
                start_time = x.hasStartDatetime.strftime("%d/%m/%Y") if x.hasStartDatetime else x.phenomenonTime.strftime("%d/%m/%Y")
                row.cell(f"{start_time}")
                row.cell(f"{x.hasEndDatetime.strftime('%d/%m/%Y') if x.hasEndDatetime else x.hasEndDatetime}")
                row.cell(f"R{x.responsibleAgent if x.responsibleAgent else 'N/A'}")


    if calendar_data.materials:
        pdf.ln()
        pdf.set_fill_color(0, 255, 255)

        pdf.set_font("FreeSerif", "B", 12)
        pdf.cell(0, 10, "Raw materials added", ln=True)
        pdf.ln(5)

        with pdf.table(text_align="CENTER", padding=0.5, v_align=VAlign.M) as table:
            row = table.row()
            pdf.set_font("FreeSerif", "B", 10)
            row.cell("Name")
            row.cell("Unit")
            row.cell("Numeric value")
            pdf.set_font("FreeSerif", "", 9)
            for material in calendar_data.materials:
                for x in material.hasCompostMaterial:
                    row = table.row()
                    pdf.set_fill_color(255, 255, 240)
                    row.cell(x.typeName)
                    row.cell(x.quantityValue.unit if x.quantityValue else 'N/A')
                    row.cell(str(x.quantityValue.numericValue) if x.quantityValue else 'N/A')

    pdf.ln(10)

    return pdf


def process_farm_calendar_data(
        token: dict[str, str],
        pdf_file_name: str,
        observation_type_name: str = None,
        data=None,
        operation_id: str = None,
        from_date: datetime.date = None,
        to_date: datetime.date = None
) -> None:
    """
    Process farm calendar data and generate PDF report
    """
    try:
        if not data:
            if not settings.REPORTING_USING_GATEKEEPER:
                raise HTTPException(
                    status_code=400,
                    detail=f"Data file must be provided if gatekeeper is not used.",
                )
            params = {"format": "json", "activity_type": ""}
            operation_url = f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["operations"]}'
            obs_url = f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["observations"]}'

            observations = []
            materials = []
            operations = []

            # No operation ID we retrieve all data from this type)
            if not operation_id:
                # Check for generic response
                if observation_type_name:
                    params["name"] = observation_type_name
                    farm_activity_type_info = make_get_request(
                        url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["activity_types"]}',
                        token=token,
                        params=params,
                    )

                    del params["name"]

                    if farm_activity_type_info:
                        params["activity_type"] = farm_activity_type_info[0]["@id"].split(":")[3]
                        decode_dates_filters(params, from_date, to_date)
                        observations = make_get_request(
                            url=obs_url,
                            token=token,
                            params=params,
                        )

                        operations = make_get_request(
                            url=operation_url,
                            token=token,
                            params=params,
                        )

            else:
                operation_url = f"{operation_url}{operation_id}/"
                del params['activity_type']

                operation_params = params.copy()
                operations = make_get_request(
                    url=operation_url,
                    token=token,
                    params=operation_params,
                )

                # Operations are not array it is only one element (ID used)
                operations = [operations] if operations else []
                if operations:
                    if not observation_type_name:
                        id = operations[0]['activityType']["@id"].split(":")[3]
                        if id:
                            farm_activity_type_info = make_get_request(
                                url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["activity_types"]}{id}/',
                                token=token,
                                params=params
                            )
                            observation_type_name = farm_activity_type_info['name']
                    for measurement in operations[0]['hasMeasurement']:
                        observation = make_get_request(
                            url=f"{obs_url}{measurement['@id'].split(':')[3]}/",
                            token=token,
                            params=params,
                        )
                        observations.append(observation)

                    if operations[0]['hasNestedOperation']:
                        material_url = (
                            f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["operations"]} \
                                        {operation_id}{settings.REPORTING_FARMCALENDAR_URLS["materials"]}')
                        materials = make_get_request(
                            url=material_url,
                            token=token,
                            params=params
                        )

            calendar_data = FarmCalendarData(
                activity_type_info=observation_type_name,
                observations=observations,
                farm_activities=operations,
                materials=materials,
                )
        else:
            dt = json.load(data.file)
            calendar_data = FarmCalendarData(
                activity_type_info=observation_type_name,
                observations=dt["observations"],
                farm_activities=dt["operations"],
                materials=dt["materials"]
            )

        pdf = create_farm_calendar_pdf(calendar_data, token)
        pdf_dir = f"{settings.PDF_DIRECTORY}{pdf_file_name}"
        os.makedirs(os.path.dirname(f"{pdf_dir}.pdf"), exist_ok=True)
        pdf.output(f"{pdf_dir}.pdf")

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error processing farm calendar data: {str(e)}"
        )
