import json
import logging
import os
from typing import Union
from fastapi import HTTPException

from core import settings
from fpdf import FontFace
from fpdf.enums import VAlign
from schemas.compost import *
from utils import EX, add_fonts
from utils.json_handler import make_get_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FarmCalendarData:
    """Class to process and store connected farm calendar data"""

    def __init__(
        self,
        activity_type_info: str,
        observations: Union[dict, str],
        farm_activities: Union[dict, str],
    ):
        self.activity_type = activity_type_info
        try:
            self.observations = [
                CropObservation.model_validate(obs) for obs in observations
            ]
            self.operations = [Operation.model_validate(act) for act in farm_activities]

        except Exception as e:
            logger.error(f"Error parsing farm calendar data: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Reporting service failed during data validation. File is not correct JSON. {e}",
            )


def create_farm_calendar_pdf(calendar_data: FarmCalendarData) -> EX:
    """Create PDF report from farm calendar data"""
    pdf = EX()
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_title("Farm Calendar Report")

    EX.ln(pdf)
    pdf.set_font("FreeSerif", "B", 14)
    pdf.cell(0, 10, "Farm Calendar Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("FreeSerif", "B", 12)
    pdf.cell(0, 10, "Activity Type Information", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Type: {calendar_data.activity_type}", ln=True)

    pdf.set_font("FreeSerif", "B", 12)
    pdf.cell(0, 10, "Operations and Observations", ln=True)
    pdf.ln(5)

    style = FontFace(fill_color=(180, 196, 36	))
    if calendar_data.operations:
        with pdf.table(text_align="CENTER", padding=0.5) as table:

            row = table.row()
            row.style = style
            pdf.set_font("FreeSerif", "B", 10)
            row.cell(f"Operation")

            row.cell(f"Details")

            row.cell(
                f"Start",
            )
            row.cell("End")
            row.cell("Responsible Agent")
            row.cell("Type")
            row.cell("Machinery IDs")
            pdf.set_font("FreeSerif", "", 9)
            style = FontFace(fill_color=(255, 255, 240			))
            for operation in calendar_data.operations:

                row = table.row()
                row.style = style

                row.cell(f"{operation.title}")

                row.cell( f"{operation.details}",)

                if operation.hasStartDatetime:
                    row.cell(
                        f"{operation.hasStartDatetime}",
                    )
                else:
                    row.cell(
                    "N/a"
                    )
                if operation.hasEndDatetime:
                    row.cell(
                        f"{operation.hasEndDatetime}",
                    )
                else:
                    row.cell(
                        f"{operation.hasEndDatetime}",
                    )
                (
                    row.cell(f"{operation.responsibleAgent}")
                    if operation.responsibleAgent
                    else row.cell(
                        f"{operation.hasEndDatetime}",
                    )
                )
                row.cell(calendar_data.activity_type)

                if operation.usesAgriculturalMachinery:
                    machinery_ids = ", ".join(
                        [
                            machinery.get("@id", "N/A").split(":")[3]
                            for machinery in operation.usesAgriculturalMachinery
                        ]
                    )
                    row.cell( f"{machinery_ids}")
                else:
                    row.cell(
                        f"{operation.hasEndDatetime}",
                    )
    if calendar_data.observations:
        pdf.ln()
        style = FontFace(fill_color=(180, 196, 36	))

        with pdf.table(text_align="CENTER", padding=0.5, v_align=VAlign.M) as table:
            row = table.row()
            row.style = style
            pdf.set_font("FreeSerif", "B", 10)
            row.cell("Value")
            row.cell("Value unit")
            row.cell("Property")
            row.cell("Observed Property")
            row.cell("Details")
            row.cell("Start")
            row.cell("End")
            row.cell("Responsible Agent")
            row.cell("Machinery IDs")
            pdf.set_font("FreeSerif", "", 9)

            for x in calendar_data.observations:
                row = table.row()
                style = FontFace(fill_color=(255, 255, 240		))
                row.style = style
                (
                    row.cell( f"{x.hasResult.hasValue}")
                    if x.hasResult
                    else row.cell("N/A")
                )
                (
                    row.cell( f"{x.hasResult.unit}")
                    if x.hasResult
                    else row.cell("N/A")
                )
                (
                    row.cell( f"{x.relatesToProperty}")
                    if x.relatesToProperty
                    else row.cell("N/A")
                )
                (
                    row.cell(f"O{x.observedProperty}")
                    if x.observedProperty
                    else row.cell("N/A")
                )
                row.cell(f"{x.details}")

                if x.hasStartDatetime:
                    row.cell(
                        f"{x.hasStartDatetime}",
                    )
                else:
                    row.cell("N/A")

                if x.hasEndDatetime:
                    row.cell(
                        f"{x.hasEndDatetime}",
                    )
                else:
                    row.cell("N/A")
                (
                    row.cell(f"Responsible: {x.responsibleAgent}")
                    if x.responsibleAgent
                    else row.cell("N/A")
                )

                if x.usesAgriculturalMachinery:
                    machinery_ids = ", ".join(
                        [
                            machinery.get("@id", "N/A").split(":")[3]
                            for machinery in x.usesAgriculturalMachinery
                        ]
                    )
                    row.cell(f"{machinery_ids}")
                else:
                    row.cell("N/A")

    pdf.ln(10)

    return pdf


def process_farm_calendar_data(
    observation_type_name: str,
    token: dict[str, str],
    pdf_file_name: str,
    data=None,
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

            params = {"format": "json", "name": observation_type_name}
            farm_activity_type_info = make_get_request(
                url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["activity_types"]}',
                token=token,
                params=params,
            )

            if not farm_activity_type_info:
                return

            del params["name"]
            params["activity_type"] = farm_activity_type_info[0]["@id"].split(":")[3]

            observations = make_get_request(
                url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["observations"]}',
                token=token,
                params=params,
            )

            farm_activities = make_get_request(
                url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["activities"]}',
                token=token,
                params=params,
            )

            calendar_data = FarmCalendarData(
                activity_type_info=observation_type_name,
                observations=observations,
                farm_activities=farm_activities,
            )
        else:
            dt = json.load(data.file)
            calendar_data = FarmCalendarData(
                activity_type_info=observation_type_name,
                observations=dt["observations"],
                farm_activities=dt["farm_activities"],
            )

        pdf = create_farm_calendar_pdf(calendar_data)
        pdf_dir = f"{settings.PDF_DIRECTORY}{pdf_file_name}"
        os.makedirs(os.path.dirname(f"{pdf_dir}.pdf"), exist_ok=True)
        pdf.output(f"{pdf_dir}.pdf")

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error processing farm calendar data: {str(e)}"
        )
