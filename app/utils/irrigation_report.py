import json
import logging
import os

from fastapi import HTTPException
from fpdf.fonts import FontFace

from core import settings
from utils import EX, add_fonts, decode_dates_filters, get_parcel_info
from schemas.irrigation import *
from utils.farm_calendar_report import geolocator
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


def create_pdf_from_operations(operations: List[IrrigationOperation], token: dict[str, str] = None):
    """
    Create PDF report from irrigation operations
    """
    pdf = EX()
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    EX.ln(pdf)

    pdf.set_font("FreeSerif", "B", 14)
    pdf.cell(0, 10, f"Irrigation Operation Report", ln=True, align="C")
    pdf.set_font("FreeSerif", style="", size=9)
    pdf.cell(0, 7, f"Data Generated - {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("FreeSerif", "B", 12)
    pdf.set_fill_color(240, 240, 240)

    y_position = pdf.get_y()
    line_end_x = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.line(pdf.l_margin, y_position, line_end_x, y_position)
    pdf.ln(5)

    if len(operations) == 1:
        op = operations[0]
        parcel_id = (
            op.operatedOn.get("@id") if op.operatedOn else None
        )
        address = ''
        farm  = ''
        if parcel_id:
            parcel = parcel_id.split(":")[3] if op.operatedOn else None
            if parcel:
                address, farm = get_parcel_info(parcel_id.split(":")[-1], token, geolocator)
        start_time = op.hasStartDatetime.strftime(
            "%d/%m/%Y") if op.hasStartDatetime else ''
        end_time = op.hasEndDatetime.strftime('%d/%m/%Y') if op.hasEndDatetime else ''
        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Star-End :")
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, f"{start_time}-{end_time}", ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Parcel Location:")
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, address, ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Farm information:", )
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, farm, ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Value info:", )
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, f"{op.hasAppliedAmount.numericValue} ({op.hasAppliedAmount.unit})", ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Responsible agent:", )
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, op.responsibleAgent, ln=True, fill=True)
    if len(operations) > 1:
        operations.sort(key=lambda x: x.hasStartDatetime)
        pdf.set_fill_color(0, 255, 255)
        with pdf.table(text_align="CENTER", padding=0.5) as table:
            row = table.row()
            pdf.set_font("FreeSerif", "B", 10)
            row.cell("Start - End")
            row.cell("Details")
            row.cell("Parcel")
            row.cell("Value info")
            row.cell("Irrigation System")
            row.cell("Responsible Agent")
            pdf.set_font("FreeSerif", "", 9)
            pdf.set_fill_color(255, 255, 240)
            for op in operations:
                # Operation Header
                row = table.row()
                start_time = op.hasStartDatetime.strftime(
                    "%d/%m/%Y") if op.hasStartDatetime else ''
                end_time = op.hasEndDatetime.strftime('%d/%m/%Y') if op.hasEndDatetime else ''
                row.cell(f"{start_time} - {end_time}")
                row.cell(op.details)

                parcel_id = (
                    op.operatedOn.get("@id") if op.operatedOn else None
                )
                address = ''
                if parcel_id:
                    parcel = parcel_id.split(":")[3] if op.operatedOn else None
                    if parcel:
                        address, _ = get_parcel_info(parcel_id.split(":")[-1], token, geolocator)
                row.cell(address)
                row.cell(f"{op.hasAppliedAmount.numericValue} ({op.hasAppliedAmount.unit})",
                )

                row.cell(op.usesIrrigationSystem)
                row.cell(
                    f"Responsible Agent: {op.responsibleAgent if op.responsibleAgent else 'N/A'}",
                )
                pdf.ln(10)

    return pdf


def process_irrigation_data(data, token: dict[str, str], pdf_file_name: str, from_date: datetime.date = None,
                            to_date: datetime.date = None,irrigation_id: str = None) -> None:
    """
    Process irrigation data and generate PDF report
    """

    if irrigation_id:
        json_data = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["irrigations"]}{irrigation_id}/',
            token=token,
            params={"format": "json"}
        )

        json_data = [json_data] if json_data else None

    else:
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
        pdf = create_pdf_from_operations(operations, token)
    except Exception:
        raise HTTPException(
            status_code=400, detail="PDF generation of irrigation report failed."
        )
    pdf_dir = f"{settings.PDF_DIRECTORY}{pdf_file_name}"
    os.makedirs(os.path.dirname(f"{pdf_dir}.pdf"), exist_ok=True)
    pdf.output(f"{pdf_dir}.pdf")
