import json
import logging
import os

from fastapi import HTTPException
from fpdf.fonts import FontFace

from core import settings
from utils import EX, add_fonts, decode_dates_filters
from schemas.irrigation import *
from utils.json_handler import make_get_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_irrigation_operations(data: dict) -> Optional[List[IrrigationOperation]]:
    """
    Parse list of irrigation operations from JSON data
    """
    try:
        return [IrrigationOperation.model_validate(item) for item in data]
    except Exception as e:
        logger.error(f"Error parsing irrigation operations: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Reporting service failed during PDF generation. File is not correct JSON. {e}",
        )


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
    style = FontFace(fill_color=(180, 196, 36))
    if operations:
        with pdf.table(text_align="CENTER", padding=0.5) as table:
            row = table.row()
            row.style = style
            pdf.set_font("FreeSerif", "B", 10)
            row.cell("Title"); row.cell("Type"); row.cell("Details"); row.cell(f"Parcel ID")
            row.cell("Start"); row.cell("End"); row.cell("Applied amount"); row.cell("Irrigation System")
            row.cell("Responsible Agent"); row.cell("Machinery IDs")
            pdf.set_font("FreeSerif", "", 9)
            style = FontFace(fill_color=(255, 255, 240		))
            for op in operations:
                # Operation Header
                row = table.row()
                row.style = style
                row.cell(op.title)

                activity_type = op.activityType.get(
                    "@id", "N/A"
                )  # You can adjust this to extract the specific part you need
                row.cell(activity_type)

                row.cell(op.details)

                parcel_id = (
                    op.operatedOn.get("@id", "N/A").split(":")[3] if op.operatedOn else "N/A"
                )
                row.cell(parcel_id)

                # Date and Time
                row.cell(
                    f"{op.hasStartDatetime if op.hasStartDatetime else 'N/A'}"
                )
                row.cell(
                    f"{op.hasEndDatetime if op.hasEndDatetime else 'N/A'}"
                )

                # Applied Amount
                row.cell(f"{op.hasAppliedAmount.numericValue} {op.hasAppliedAmount.unit}",
                )

                # Irrigation System
                row.cell(
                    f"{op.usesIrrigationSystem}")

                # Responsible Agent
                row.cell(
                    f"Responsible Agent: {op.responsibleAgent if op.responsibleAgent else 'N/A'}",
                )

                # Machinery IDs (if any)
                if op.usesAgriculturalMachinery:
                    machinery_ids = ", ".join(
                        [
                            machinery.get("@id", "N/A").split(":")[3]
                            for machinery in op.usesAgriculturalMachinery
                        ]
                    )
                    row.cell( f"Machinery IDs: {machinery_ids}")
                else:
                    row.cell("N/A")
                pdf.ln(10)

    return pdf


def process_irrigation_data(data, token: dict[str, str], pdf_file_name: str, from_date: datetime.date = None,
                            to_date: datetime.date = None) -> None:
    """
    Process irrigation data and generate PDF report
    """

    if not data:
        params = {"format": "json"}
        decode_dates_filters(params, from_date, to_date)
        json_data = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["irrigations"]}',
            token=token,
            params=params,
        )

    else:
        json_data = json.load(data.file)

    operations = parse_irrigation_operations(json_data)

    try:
        pdf = create_pdf_from_operations(operations)
    except Exception:
        raise HTTPException(
            status_code=400, detail="PDF generation of irrigation report failed."
        )
    pdf_dir = f"{settings.PDF_DIRECTORY}{pdf_file_name}"
    os.makedirs(os.path.dirname(f"{pdf_dir}.pdf"), exist_ok=True)
    pdf.output(f"{pdf_dir}.pdf")
