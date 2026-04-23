import datetime
import io
import logging
import os

from fastapi import HTTPException
from geopy.geocoders import Nominatim

from core import settings
from schemas import IrrigationOperation, FertilizationOperation, CropProtectionOperation
from schemas.compost import CropObservation
from utils import (
    EX,
    add_fonts,
    decode_dates_filters,
    display_pdf_parcel_details,
    FarmInfo,
)
from utils.generate_aggregation_data import get_pest_from_obj
from utils.json_handler import make_get_request
from utils.satellite_image_get import fetch_wms_image, SatelliteImageException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

geolocator = Nominatim(user_agent="reporting_open_agri_app", timeout=5)


def _fetch_list(url_key: str, token: str, params: dict) -> list:
    """Generic list fetch from farmcalendar. Returns [] on any failure."""
    result = make_get_request(
        url=f"{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS[url_key]}",
        token=token,
        params=params,
    )
    return result if isinstance(result, list) else []


def _base_params(parcel_id: str, from_date, to_date) -> dict:
    params = {"format": "json"}
    if parcel_id:
        params["parcel"] = parcel_id
    decode_dates_filters(params, from_date, to_date)
    return params


def _fetch_crops_for_parcel(parcel_id: str, token: str) -> list:
    """Fetch all crops linked via hasAgriCrop on the parcel. Returns [] on any failure."""
    if not parcel_id:
        return []
    parcel_data = make_get_request(
        url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["parcel"]}{parcel_id}/',
        token=token,
        params={"format": "json"},
    )
    if not parcel_data or not isinstance(parcel_data, dict):
        return []
    has_agri_crop = parcel_data.get("hasAgriCrop") or []
    if not has_agri_crop:
        return []
    crops = []
    for crop_ref in has_agri_crop:
        crop_id_full = (crop_ref or {}).get("@id", "")
        if not crop_id_full:
            continue
        crop_uuid = crop_id_full.split(":")[-1]
        if not crop_uuid:
            continue
        crop_data = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["crops"]}{crop_uuid}/',
            token=token,
            params={"format": "json"},
        )
        if crop_data and isinstance(crop_data, dict):
            crops.append(crop_data)
    return crops


def _fetch_forecasting(token: str, parcel_id: str) -> list:
    """Fetch pest-risk forecasting data. Returns [] when not configured or unavailable."""
    if not settings.REPORTING_FORECASTING_BASE_URL:
        return []
    params = {"format": "json"}
    if parcel_id:
        params["parcel"] = parcel_id
    pest_risk_path = settings.REPORTING_FORECASTING_URLS.get("pest_risk", "/PestRisk/")
    result = make_get_request(
        url=f"{settings.REPORTING_FORECASTING_BASE_URL}{pest_risk_path}",
        token=token,
        params=params,
    )
    return result if isinstance(result, list) else []


def _section_header(pdf: EX, number: str, title: str) -> None:
    pdf.ln(4)
    y = pdf.get_y()
    pdf.set_fill_color(240, 240, 240)
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.set_font("FreeSerif", "B", 13)
    pdf.set_x(pdf.l_margin + 2)
    pdf.cell(0, 10, f"{number}. {title}", ln=True)
    pdf.ln(2)


def _kv(pdf: EX, label: str, value: str) -> None:
    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(52, 7, label)
    pdf.set_font("FreeSerif", "", 10)
    pdf.multi_cell(0, 7, value or "\u2014", ln=True)


def _no_data(pdf: EX, msg: str) -> None:
    pdf.set_font("FreeSerif", "", 10)
    pdf.cell(0, 8, msg, ln=True)


def _render_crops_section(pdf: EX, crops: list) -> None:
    pdf.ln(3)
    pdf.set_font("FreeSerif", "B", 11)
    pdf.cell(0, 8, "Crops", ln=True)
    pdf.ln(1)
    if not crops:
        _no_data(pdf, "No crops associated with this parcel.")
        return
    pdf.set_font("FreeSerif", "B", 10)
    with pdf.table(text_align="CENTER") as table:
        row = table.row()
        row.cell("Name")
        row.cell("Description")
        row.cell("Status")
        row.cell("Growth Stage")
        row.cell("Species")
        row.cell("Variety")
        pdf.set_font("FreeSerif", "", 9)
        for crop in crops:
            crop_species = crop.get("cropSpecies") or {}
            row = table.row()
            row.cell(crop.get("name") or "\u2014")
            row.cell(crop.get("description") or "\u2014")
            row.cell(str(crop["status"]) if crop.get("status") is not None else "\u2014")
            row.cell(crop.get("growth_stage") or "\u2014")
            row.cell(crop_species.get("name") or "\u2014")
            row.cell(crop_species.get("variety") or "\u2014")


def create_field_notebook_pdf(
    parcel_id: str,
    token: str,
    from_date=None,
    to_date=None,
    irrigation_ops: list = None,
    fertilization_ops: list = None,
    pesticide_ops: list = None,
    observations: list = None,
    forecasting_data: list = None,
    crops: list = None,
    cert_type: str = None,
    cert_number: str = None,
    cert_issuing_body: str = None,
    cert_issue_date: str = None,
    cert_expiry_date: str = None,
    cert_notes: str = None,
    include_irrigation: bool = True,
    include_fertilization: bool = True,
    include_pesticides: bool = True,
    include_observations: bool = True,
) -> EX:
    irrigation_ops = irrigation_ops or []
    fertilization_ops = fertilization_ops or []
    pesticide_ops = pesticide_ops or []
    observations = observations or []
    forecasting_data = forecasting_data or []
    crops = crops or []

    pdf = EX()
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.ln(2)

    today = datetime.datetime.now().strftime("%d/%m/%Y")
    from_str = from_date.strftime("%d/%m/%Y") if from_date else "\u2014"
    to_str = to_date.strftime("%d/%m/%Y") if to_date else today

    pdf.set_font("FreeSerif", "B", 18)
    pdf.cell(0, 12, "Field Notebook", ln=True, align="C")
    pdf.set_font("FreeSerif", "", 9)
    pdf.cell(
        0, 6,
        f"Generated: {today}     |     Reporting period: {from_str} \u2013 {to_str}",
        ln=True, align="C",
    )
    pdf.ln(4)
    y = pdf.get_y()
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)

    _section_header(pdf, "1", "Farm & Parcel Information")

    parcel_data = None
    if parcel_id and settings.REPORTING_USING_GATEKEEPER:
        parcel_data = display_pdf_parcel_details(pdf, parcel_id, geolocator, token)
    else:
        _no_data(pdf, "Parcel details require Gatekeeper mode to be enabled.")

    _render_crops_section(pdf, crops)

    if parcel_data and parcel_data.lat and parcel_data.long:
        try:
            image_bytes = fetch_wms_image(parcel_data.lat, parcel_data.long)
            pdf.ln(2)
            x_start = (pdf.w - 120) / 2
            pdf.set_x(x_start)
            pdf.image(io.BytesIO(image_bytes), type="png", w=120)
            pdf.ln(2)
        except SatelliteImageException:
            logger.info("Satellite image unavailable, continuing without it.")

    pdf.add_page()
    _section_header(pdf, "2", "Forecasting Models \u2013 Last 15 Days")

    if not forecasting_data:
        _no_data(pdf, "No forecasting data available (service not configured or no data returned).")
    else:
        pdf.set_font("FreeSerif", "B", 10)
        with pdf.table(text_align="CENTER") as table:
            row = table.row()
            row.cell("Pest / Model")
            row.cell("Risk Level")
            row.cell("Date")
            row.cell("Notes")
            pdf.set_font("FreeSerif", "", 9)
            for entry in forecasting_data:
                row = table.row()
                row.cell(str(entry.get("pest") or entry.get("name") or "\u2014"))
                row.cell(str(entry.get("riskLevel") or entry.get("risk_level") or "\u2014"))
                row.cell(str(entry.get("date") or "\u2014"))
                row.cell(str(entry.get("notes") or entry.get("details") or "\u2014"))

    _sec = [3]

    def _next_sec() -> str:
        n = str(_sec[0])
        _sec[0] += 1
        return n

    if include_pesticides:
        pdf.add_page()
        _section_header(pdf, _next_sec(), "Pest Treatment Activities")

        if not pesticide_ops:
            _no_data(pdf, "No pesticide treatment activities recorded for this period.")
        else:
            try:
                pesticide_ops.sort(key=lambda x: x.hasStartDatetime or datetime.datetime.min)
            except Exception:
                pass
            pdf.set_font("FreeSerif", "B", 10)
            with pdf.table(text_align="CENTER") as table:
                row = table.row()
                row.cell("Date")
                row.cell("Title")
                row.cell("Pesticide")
                row.cell("Dose")
                row.cell("Unit")
                row.cell("Agent")
                pdf.set_font("FreeSerif", "", 9)
                for op in pesticide_ops:
                    row = table.row()
                    row.cell(
                        op.hasStartDatetime.strftime("%d/%m/%Y")
                        if op.hasStartDatetime else "\u2014"
                    )
                    row.cell(op.title or "\u2014")
                    row.cell(get_pest_from_obj(op, token) or "\u2014")
                    row.cell(
                        str(op.hasAppliedAmount.numericValue)
                        if op.hasAppliedAmount else "\u2014"
                    )
                    row.cell(
                        op.hasAppliedAmount.unit
                        if op.hasAppliedAmount else "\u2014"
                    )
                    row.cell(op.responsibleAgent or "\u2014")

    if include_fertilization:
        pdf.add_page()
        _section_header(pdf, _next_sec(), "Fertilization Activities")

        if not fertilization_ops:
            _no_data(pdf, "No fertilization activities recorded for this period.")
        else:
            try:
                fertilization_ops.sort(key=lambda x: x.hasStartDatetime or datetime.datetime.min)
            except Exception:
                pass
            pdf.set_font("FreeSerif", "B", 10)
            with pdf.table(text_align="CENTER") as table:
                row = table.row()
                row.cell("Date")
                row.cell("Title")
                row.cell("Fertilizer")
                row.cell("Application Method")
                row.cell("Dose")
                row.cell("Unit")
                row.cell("Agent")
                pdf.set_font("FreeSerif", "", 9)
                for op in fertilization_ops:
                    row = table.row()
                    row.cell(
                        op.hasStartDatetime.strftime("%d/%m/%Y")
                        if op.hasStartDatetime else "\u2014"
                    )
                    row.cell(op.title or "\u2014")
                    fertilizer_name = "\u2014"
                    if op.usesFertilizer:
                        fertilizer_name = (
                            op.usesFertilizer.get("name")
                            or op.usesFertilizer.get("@id", "").split(":")[-1]
                            or "Yes"
                        )
                    row.cell(fertilizer_name)
                    row.cell(op.hasApplicationMethod or "\u2014")
                    row.cell(
                        str(op.hasAppliedAmount.numericValue)
                        if op.hasAppliedAmount else "\u2014"
                    )
                    row.cell(
                        op.hasAppliedAmount.unit
                        if op.hasAppliedAmount else "\u2014"
                    )
                    row.cell(op.responsibleAgent or "\u2014")

    if include_irrigation:
        pdf.add_page()
        _section_header(pdf, _next_sec(), "Irrigation Activities")

        if not irrigation_ops:
            _no_data(pdf, "No irrigation activities recorded for this period.")
        else:
            try:
                irrigation_ops.sort(key=lambda x: x.hasStartDatetime or datetime.datetime.min)
            except Exception:
                pass
            pdf.set_font("FreeSerif", "B", 10)
            with pdf.table(text_align="CENTER") as table:
                row = table.row()
                row.cell("Start Date")
                row.cell("End Date")
                row.cell("Title")
                row.cell("Irrigation System")
                row.cell("Dose")
                row.cell("Unit")
                row.cell("Agent")
                pdf.set_font("FreeSerif", "", 9)
                for op in irrigation_ops:
                    row = table.row()
                    row.cell(
                        op.hasStartDatetime.strftime("%d/%m/%Y")
                        if op.hasStartDatetime else "\u2014"
                    )
                    row.cell(
                        op.hasEndDatetime.strftime("%d/%m/%Y")
                        if op.hasEndDatetime else "\u2014"
                    )
                    row.cell(op.title or "\u2014")
                    sys_name = "\u2014"
                    if isinstance(op.usesIrrigationSystem, dict):
                        sys_name = op.usesIrrigationSystem.get("name") or "\u2014"
                    elif op.usesIrrigationSystem:
                        sys_name = op.usesIrrigationSystem
                    row.cell(sys_name)
                    row.cell(
                        str(op.hasAppliedAmount.numericValue)
                        if op.hasAppliedAmount else "\u2014"
                    )
                    row.cell(
                        op.hasAppliedAmount.unit
                        if op.hasAppliedAmount else "\u2014"
                    )
                    row.cell(op.responsibleAgent or "\u2014")

    if include_observations:
        pdf.add_page()
        _section_header(pdf, _next_sec(), "Crop Data & Observations")

        if not observations:
            _no_data(pdf, "No observations recorded for this period.")
        else:
            try:
                observations.sort(
                    key=lambda x: x.hasStartDatetime or x.phenomenonTime or datetime.datetime.min
                )
            except Exception:
                pass
            pdf.set_font("FreeSerif", "B", 10)
            with pdf.table(text_align="CENTER") as table:
                row = table.row()
                row.cell("Date")
                row.cell("Title")
                row.cell("Observed Property")
                row.cell("Value")
                row.cell("Unit")
                row.cell("Details")
                pdf.set_font("FreeSerif", "", 9)
                for obs in observations:
                    row = table.row()
                    date_val = obs.hasStartDatetime or obs.phenomenonTime
                    row.cell(
                        date_val.strftime("%d/%m/%Y") if date_val else "\u2014"
                    )
                    row.cell(obs.title or "\u2014")
                    row.cell(obs.observedProperty or "\u2014")
                    row.cell(
                        str(obs.hasResult.hasValue)
                        if obs.hasResult and obs.hasResult.hasValue else "\u2014"
                    )
                    row.cell(
                        obs.hasResult.unit
                        if obs.hasResult and obs.hasResult.unit else "\u2014"
                    )
                    row.cell(obs.details or "\u2014")

    pdf.ln(8)
    pdf.set_font("FreeSerif", "B", 12)
    pdf.cell(0, 8, "Quality Certification", ln=True)
    y = pdf.get_y()
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(4)
    cert_fields = [
        ("Certification Type", cert_type),
        ("Certification Number / Reference", cert_number),
        ("Issuing Body", cert_issuing_body),
        ("Issue Date", cert_issue_date),
        ("Expiry Date", cert_expiry_date),
        ("Notes", cert_notes),
    ]
    for label, value in cert_fields:
        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(72, 9, f"{label}:")
        pdf.set_font("FreeSerif", "", 10)
        if value:
            pdf.multi_cell(0, 9, value, ln=True)
        else:
            pdf.cell(0, 9, "_____________________________________________", ln=True)
        pdf.ln(1)

    return pdf


def process_field_notebook_data(
    token: str,
    pdf_file_name: str,
    parcel_id: str = None,
    from_date: datetime.date = None,
    to_date: datetime.date = None,
    cert_type: str = None,
    cert_number: str = None,
    cert_issuing_body: str = None,
    cert_issue_date: str = None,
    cert_expiry_date: str = None,
    cert_notes: str = None,
    include_irrigation: bool = True,
    include_fertilization: bool = True,
    include_pesticides: bool = True,
    include_observations: bool = True,
) -> None:
    """
    Fetch all field activity data for a parcel and generate a unified Field Notebook PDF.
    """
    if not settings.REPORTING_USING_GATEKEEPER:
        raise HTTPException(
            status_code=400,
            detail="Field Notebook report requires Gatekeeper mode (data is fetched from Farm Calendar service).",
        )

    params = _base_params(parcel_id, from_date, to_date)

    crops = _fetch_crops_for_parcel(parcel_id, token)

    raw_irrigations = _fetch_list("irrigations", token, params) if include_irrigation else []
    raw_fertilizations = _fetch_list("fertilization", token, params) if include_fertilization else []
    raw_pesticides = _fetch_list("pesticides", token, params) if include_pesticides else []

    raw_observations = _fetch_list("observations", token, params) if include_observations else []

    forecasting_data = _fetch_forecasting(token, parcel_id)

    try:
        irrigation_ops = [IrrigationOperation.model_validate(item) for item in raw_irrigations]
    except Exception as e:
        logger.error(f"Error parsing irrigation operations: {e}")
        irrigation_ops = []

    try:
        fertilization_ops = [FertilizationOperation.model_validate(item) for item in raw_fertilizations]
    except Exception as e:
        logger.error(f"Error parsing fertilization operations: {e}")
        fertilization_ops = []

    try:
        pesticide_ops = [CropProtectionOperation.model_validate(item) for item in raw_pesticides]
    except Exception as e:
        logger.error(f"Error parsing pesticide operations: {e}")
        pesticide_ops = []

    try:
        observations = [CropObservation.model_validate(item) for item in raw_observations]
    except Exception as e:
        logger.error(f"Error parsing observations: {e}")
        observations = []

    try:
        pdf = create_field_notebook_pdf(
            parcel_id=parcel_id,
            token=token,
            from_date=from_date,
            to_date=to_date,
            irrigation_ops=irrigation_ops,
            fertilization_ops=fertilization_ops,
            pesticide_ops=pesticide_ops,
            observations=observations,
            forecasting_data=forecasting_data,
            crops=crops,
            cert_type=cert_type,
            cert_number=cert_number,
            cert_issuing_body=cert_issuing_body,
            cert_issue_date=cert_issue_date,
            cert_expiry_date=cert_expiry_date,
            cert_notes=cert_notes,
            include_irrigation=include_irrigation,
            include_fertilization=include_fertilization,
            include_pesticides=include_pesticides,
            include_observations=include_observations,
        )
    except Exception as e:
        logger.error(f"Field Notebook PDF generation failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Field Notebook PDF generation failed: {e}",
        )

    pdf_dir = f"{settings.PDF_DIRECTORY}{pdf_file_name}"
    os.makedirs(os.path.dirname(f"{pdf_dir}.pdf"), exist_ok=True)
    pdf.output(f"{pdf_dir}.pdf")
