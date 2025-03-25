import logging
from typing import Union
from fastapi import HTTPException

from schemas.compost import *
from utils import EX, add_fonts

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

    for operation in calendar_data.operations:
        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(0, 10, f"Operation: {operation.title}", ln=True)

        pdf.set_font("FreeSerif", "", 9)
        pdf.multi_cell(0, 10, f"Details: {operation.details}", ln=True)
        pdf.cell(
            0,
            10,
            f"Start: {operation.hasStartDatetime if operation.hasStartDatetime else 'N/A'}",
            ln=True,
        )
        pdf.cell(
            0,
            10,
            f"End: {operation.hasEndDatetime if operation.hasEndDatetime else 'N/A'}",
            ln=True,
        )
        (
            pdf.cell(0, 10, f"Responsible: {operation.responsibleAgent}", ln=True)
            if operation.responsibleAgent
            else None
        )
        pdf.cell(0, 10, f"Type: {operation.activity_type.get('@id', 'N/A')}", ln=True)

        if operation.usesAgriculturalMachinery:
            machinery_ids = ", ".join(
                [
                    machinery.get("@id", "N/A").split(":")[3]
                    for machinery in operation.usesAgriculturalMachinery
                ]
            )
            pdf.cell(0, 10, f"Machinery IDs: {machinery_ids}", ln=True)

        for x in calendar_data.observations:
            pdf.set_font("FreeSerif", "B", 10)
            pdf.cell(0, 10, "Observations:", ln=True)
            pdf.set_font("FreeSerif", "", 10)
            pdf.cell(0, 10, f"Value: {x.hasValue}", ln=True)
            pdf.cell(0, 10, f"Property: {x.relatesToProperty}", ln=True)
            pdf.cell(0, 10, f"Details: {x.details}", ln=True)
            pdf.cell(
                0,
                10,
                f"Start: {x.hasStartDatetime if x.hasStartDatetime else 'N/A'}",
                ln=True,
            )
            pdf.cell(
                0,
                10,
                f"End: {x.hasEndDatetime if x.hasEndDatetime else 'N/A'}",
                ln=True,
            )
            (
                pdf.cell(0, 10, f"Responsible: {x.responsibleAgent}", ln=True)
                if x.responsibleAgent
                else None
            )

            if x.usesAgriculturalMachinery:
                machinery_ids = ", ".join(
                    [
                        machinery.get("@id", "N/A").split(":")[3]
                        for machinery in x.usesAgriculturalMachinery
                    ]
                )
                pdf.cell(0, 10, f"Machinery IDs: {machinery_ids}", ln=True)

        pdf.ln(10)

    return pdf


def process_farm_calendar_data(
    activity_type_info: str,
    observations: Union[dict, str],
    farm_activities: Union[dict, str],
) -> EX:
    """
    Process farm calendar data and generate PDF report
    """
    try:
        calendar_data = FarmCalendarData(
            activity_type_info=activity_type_info,
            observations=observations,
            farm_activities=farm_activities,
        )

        pdf = create_farm_calendar_pdf(calendar_data)
        return pdf

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing farm calendar data: {str(e)}"
        )
