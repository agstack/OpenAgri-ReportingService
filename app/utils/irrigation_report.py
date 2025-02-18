import logging
from typing import Union, Optional

from utils import EX, add_fonts
from schemas.irrigation import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_irrigation_operations(
    data: Union[dict, str],
) -> Optional[List[IrrigationOperation]]:
    """
    Parse list of irrigation operations from JSON data
    """
    try:
        return [IrrigationOperation.model_validate(item) for item in data]
    except Exception as e:
        logger.info(f"Error parsing irrigation operations: {e}")
        return None


def create_pdf_from_operations(operations: List[IrrigationOperation]):
    """
    Create PDF report from irrigation operations
    """
    pdf = EX()
    pdf.add_page()
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_title("Irrigation Operations Report")
    EX.ln(pdf)

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "Irrigation Operations Report")
    pdf.ln(10)

    for op in operations:
        # Operation Header
        pdf.set_font("FreeSerif", "B", 9)
        pdf.cell(0, 10, f"Operation: {op.title}", ln=True)

        # Details
        pdf.set_font("FreeSerif", "", 9)
        pdf.multi_cell(0, 10, f"Details: {op.details}")
        pdf.ln(5)

        pdf.cell(0, 10, f"Operated on Parcel: {op.operatedOn.split(':')[3]}", ln=True)
        pdf.cell(0, 10, f"Start: {op.hasStartDatetime}", ln=True)
        pdf.cell(0, 10, f"End: {op.hasEndDatetime}", ln=True)

        pdf.cell(
            0,
            10,
            f"Applied Amount: {op.hasAppliedAmount.numericValue} {op.hasAppliedAmount.unit}",
            ln=True,
        )

        pdf.cell(0, 10, f"Irrigation System: {op.usesIrrigationSystem}", ln=True)
        pdf.cell(0, 10, f"Responsible Agent: {op.responsibleAgent}", ln=True)

        if op.usesAgriculturalMachinery:
            pdf.cell(
                0,
                10,
                f"Machinery IDs: {', '.join(op.usesAgriculturalMachinery).split(':')[3]}",
                ln=True,
            )

        pdf.ln(10)

    return pdf


def process_irrigation_data(json_data: Union[dict, str]):
    """
    Process irrigation data and generate PDF report
    """

    operations = parse_irrigation_operations(json_data)

    if not operations:
        return None

    pdf = create_pdf_from_operations(operations)

    return pdf
