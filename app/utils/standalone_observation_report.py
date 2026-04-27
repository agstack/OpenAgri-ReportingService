import datetime
import io
import json
import logging
import os
from typing import List, Optional

from fastapi import HTTPException
from fpdf.enums import VAlign

from core import settings
from schemas import CropObservation, ManualFarmInfo, ManualParcelInfo
from utils import EX, add_fonts
from utils.satellite_image_get import SatelliteImageException, fetch_wms_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _parse_observations(raw) -> List[CropObservation]:
    if not isinstance(raw, list):
        raise HTTPException(
            status_code=400,
            detail="Observations payload must be a JSON array of observation JSON-LD objects.",
        )
    try:
        return [CropObservation.model_validate(item) for item in raw]
    except Exception as e:
        logger.error(f"Error parsing standalone observations: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Reporting service failed during observation validation. {e}",
        )


def _render_farm_details(
    pdf: EX,
    parcel: ManualParcelInfo,
    farm: ManualFarmInfo,
    from_date: Optional[datetime.date],
    to_date: Optional[datetime.date],
):
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    from_date_local = from_date.strftime("%Y-%m-%d") if from_date else today
    to_date_local = to_date.strftime("%Y-%m-%d") if to_date else ""

    pdf.set_font("FreeSerif", "B", 15)
    pdf.set_x((pdf.w / 4) - 30)
    pdf.cell(30, 8, "1. Farm Details", align="L")
    pdf.multi_cell(0, 8, "", ln=True, fill=False)

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 8, "Reporting Period")
    pdf.set_font("FreeSerif", "", 10)
    pdf.multi_cell(0, 8, f"{from_date_local} / {to_date_local}", ln=True, fill=True)

    rows = [
        ("Parcel Location:", parcel.address),
        ("Parcel Identifier:", parcel.identifier),
        ("Parcel Area (m2):", f"{parcel.area}" if parcel.area else ""),
        ("Farm Name:", farm.name),
        ("Municipality:", farm.municipality),
        ("Administrator:", farm.administrator),
        ("Contact Person:", farm.contactPerson),
        ("Farm VAT:", farm.vatID),
        ("Farm Description:", farm.description),
    ]
    for label, value in rows:
        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, label)
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, value or "", ln=True, fill=True)

    if parcel.lat is not None and parcel.lng is not None:
        try:
            image_bytes = fetch_wms_image(parcel.lat, parcel.lng)
            image_file = io.BytesIO(image_bytes)
            pdf.ln(2)
            x_start = (pdf.w - 100) / 2
            pdf.set_x(x_start)
            pdf.image(image_file, type="png", w=100)
        except SatelliteImageException:
            logger.info("Satellite image issue happened, continue without image.")


def _render_observation_table(pdf: EX, observations: List[CropObservation]):
    if not observations:
        pdf.ln(4)
        pdf.set_font("FreeSerif", "", 10)
        pdf.cell(0, 8, "No observations provided.", ln=True)
        return

    observations.sort(
        key=lambda o: o.hasStartDatetime
        or o.phenomenonTime
        or datetime.datetime.min
    )

    pdf.add_page()
    pdf.set_font("FreeSerif", "B", 15)
    pdf.set_x((pdf.w / 4) - 30)
    pdf.cell(30, 8, "2. Observations", align="L", ln=True)
    pdf.ln(4)

    pdf.set_fill_color(0, 255, 255)
    with pdf.table(text_align="CENTER", padding=0.5, v_align=VAlign.M) as table:
        row = table.row()
        pdf.set_font("FreeSerif", "B", 10)
        row.cell("Start - End")
        row.cell("Observed Property")
        row.cell("Value")
        row.cell("Unit")
        row.cell("Responsible Agent")
        row.cell("Details")
        pdf.set_font("FreeSerif", "", 9)
        pdf.set_fill_color(255, 255, 240)
        for obs in observations:
            row = table.row()
            start = obs.hasStartDatetime or obs.phenomenonTime
            end = obs.hasEndDatetime
            start_str = start.strftime("%d/%m/%Y") if start else ""
            end_str = end.strftime("%d/%m/%Y") if end else ""
            row.cell(f"{start_str} - {end_str}".strip(" -"))
            row.cell(obs.observedProperty or "")
            value = obs.hasResult.hasValue if obs.hasResult and obs.hasResult.hasValue else ""
            unit = obs.hasResult.unit if obs.hasResult and obs.hasResult.unit else ""
            row.cell(str(value))
            row.cell(unit)
            row.cell(obs.responsibleAgent or "")
            row.cell(obs.details or "")


def create_standalone_observation_pdf(
    observations: List[CropObservation],
    parcel: ManualParcelInfo,
    farm: ManualFarmInfo,
    title: str,
    from_date: Optional[datetime.date],
    to_date: Optional[datetime.date],
) -> EX:
    pdf = EX()
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    EX.ln(pdf)

    pdf.set_font("FreeSerif", "B", 14)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.set_font("FreeSerif", style="", size=9)
    pdf.cell(
        0,
        7,
        f"Data Generated - {datetime.datetime.now().strftime('%d/%m/%Y')}",
        ln=True,
        align="C",
    )
    pdf.ln(5)

    y_position = pdf.get_y()
    line_end_x = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.line(pdf.l_margin, y_position, line_end_x, y_position)
    pdf.ln(5)

    pdf.set_fill_color(240, 240, 240)
    _render_farm_details(pdf, parcel, farm, from_date, to_date)
    _render_observation_table(pdf, observations)
    pdf.ln(10)
    return pdf


def process_standalone_observation_data(
    data: bytes,
    pdf_file_name: str,
    parcel: ManualParcelInfo,
    farm: ManualFarmInfo,
    title: str = "Observation Report",
    from_date: Optional[datetime.date] = None,
    to_date: Optional[datetime.date] = None,
) -> None:
    try:
        if not data:
            raise HTTPException(
                status_code=400,
                detail="Observation JSON-LD payload is required.",
            )

        try:
            payload = json.loads(data)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON payload for observations: {e}",
            )

        observations = _parse_observations(payload)

        pdf = create_standalone_observation_pdf(
            observations=observations,
            parcel=parcel,
            farm=farm,
            title=title,
            from_date=from_date,
            to_date=to_date,
        )
        pdf_dir = f"{settings.PDF_DIRECTORY}{pdf_file_name}"
        os.makedirs(os.path.dirname(f"{pdf_dir}.pdf"), exist_ok=True)
        pdf.output(f"{pdf_dir}.pdf")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing standalone observation data: {str(e)}",
        )
