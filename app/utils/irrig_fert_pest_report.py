import io
import json
import logging
import os
from datetime import datetime
from typing import Optional, List

from fastapi import HTTPException

from core import settings
from schemas import IrrigationOperation, FertilizationOperation, CropProtectionOperation
from utils.satellite_image_get import fetch_wms_image, SatelliteImageException
from utils import EX, add_fonts, decode_dates_filters, get_parcel_info, display_pdf_parcel_details
from utils.farm_calendar_report import geolocator
from utils.generate_aggregation_data import (
    generate_total_volume_graph,
    generate_amount_per_hectare,
    prepare_df_for_calculations,
    generate_aggregation_table_data,
    get_pest_from_obj,
    pesticides_aggregation,
)
from utils.json_handler import make_get_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_irrig_fert_operations(
    data: dict,
    irrigation_flag: bool = True,
    fertilization_flag: bool = False,
) -> Optional[
    List[IrrigationOperation | FertilizationOperation | CropProtectionOperation]
]:
    """
    Parse list of irrigation or fertilization operations from JSON data
    """
    try:
        if irrigation_flag:
            return [IrrigationOperation.model_validate(item) for item in data]
        elif fertilization_flag:
            return [FertilizationOperation.model_validate(item) for item in data]
        else:
            return [CropProtectionOperation.model_validate(item) for item in data]
    except Exception as e:
        logger.error(f"Error parsing irrigation/fertilization operations: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Reporting service failed during PDF generation. File is not correct JSON. {e}",
        )


def create_pdf_from_operations(
    operations: List[IrrigationOperation]
    | List[FertilizationOperation | CropProtectionOperation],
    token: dict[str, str] = None,
    data_used: bool = False,
    parcel_id: str = None,
    from_date: datetime.date = None,
    to_date: datetime.date = None,
    irrigation_flag: bool = True,
    fertilization_flag: bool = False,
):
    """
    Create PDF report from irrigation operations
    """
    pdf = EX()
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    EX.ln(pdf)

    today = datetime.now().strftime("%d/%m/%Y")
    pdf.set_font("FreeSerif", "B", 14)
    title = "Pesticide"
    if irrigation_flag:
        title = "Irrigation"
    elif fertilization_flag:
        title = "Fertilization"

    pdf.cell(0, 10, f"{title} Operation Report", ln=True, align="C")
    pdf.set_font("FreeSerif", style="", size=9)
    pdf.cell(
        0,
        7,
        f"Data Generated - {today}",
        ln=True,
        align="C",
    )
    pdf.ln(5)

    pdf.set_font("FreeSerif", "B", 12)
    pdf.set_fill_color(240, 240, 240)

    y_position = pdf.get_y()
    line_end_x = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.line(pdf.l_margin, y_position, line_end_x, y_position)
    pdf.ln(5)

    address, farm, parcel_defined = None, None, None
    from_date_local, to_date_local = today, None
    if from_date:
        from_date_local = from_date.strftime("%Y-%m-%d")

    if to_date:
        to_date_local = to_date.strftime("%Y-%m-%d")
    else:
        to_date_local = ""


    pdf.set_font("FreeSerif", "B", 15)
    pdf.set_x((pdf.w/4)-30  )
    pdf.cell(30, 8, "1. Farm Details", align='L')
    pdf.multi_cell(0, 8, f"", ln=True, fill=False)
    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 8, "Reporting Period")
    pdf.set_font("FreeSerif", "", 10)
    pdf.multi_cell(0, 8, f"{from_date_local} / {to_date_local}", ln=True, fill=True)

    if parcel_id:
        parcel_data = display_pdf_parcel_details(pdf, parcel_id, geolocator, token)
        if parcel_data.long != 0 and parcel_data.lat != 0:
            try:
                image_bytes = fetch_wms_image(parcel_data.lat, parcel_data.long)
                image_file = io.BytesIO(image_bytes)
                pdf.ln(2)
                x_start = (pdf.w - 100) / 2
                pdf.set_x(x_start)
                pdf.image(image_file, type="png", w=100)
            except SatelliteImageException:
                logger.info("Satellite image issue happened, continue without image.")
        parcel_defined = True

    if len(operations) == 1:
        op = operations[0]
        if not parcel_defined:
            parcel_id = op.operatedOn.get("@id") if op.operatedOn else None
            identifier = ""
            if parcel_id:
                parcel = parcel_id.split(":")[3] if op.operatedOn else None
                if parcel:
                    parcel_data, farm, identifier = get_parcel_info(
                        parcel_id.split(":")[-1],
                        token,
                        geolocator,
                        identifier_flag=True,
                    )
                    address = parcel_data.address
        start_time = (
            op.hasStartDatetime.strftime("%d/%m/%Y") if op.hasStartDatetime else ""
        )
        end_time = op.hasEndDatetime.strftime("%d/%m/%Y") if op.hasEndDatetime else ""
        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Star-End :")
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, f"{start_time}-{end_time}", ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Parcel Location:")
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, address, ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 8, "Parcel Identifier:")
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, identifier, ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(
            40,
            8,
            "Farm Location:",
        )
        pdf.set_font("FreeSerif", "", 10)
        farm_local = f"Name: {farm.name} | Municipality: {farm.municipality}"
        pdf.multi_cell(0, 8, farm_local, ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(
            40,
            8,
            "Administrator:",
        )
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, farm.administrator, ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(
            40,
            8,
            "Contact Person:",
        )
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, farm.contactPerson, ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(
            40,
            8,
            "Farm vat:",
        )
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, farm.vatID, ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(
            40,
            8,
            "Farm Description:",
        )
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(0, 8, farm.description, ln=True, fill=True)

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(
            40,
            8,
            "Value info:",
        )
        pdf.set_font("FreeSerif", "", 10)
        pdf.multi_cell(
            0,
            8,
            f"{op.hasAppliedAmount.numericValue} ({op.hasAppliedAmount.unit})",
            fill=True,
        )

    if len(operations) > 1:
        if not data_used:
            operations.sort(key=lambda x: x.hasStartDatetime)
        pdf.set_font("FreeSerif", "B", 15)
        pdf.ln(2)
        pdf.set_x((pdf.w / 4) - 30)
        pdf.cell(30, 2,f"2. {title}s", align='L', ln=True)
        pdf.set_fill_color(0, 255, 255)
        pdf.ln(4)
        with pdf.table(text_align="CENTER") as table:
            row = table.row()
            pdf.set_font("FreeSerif", "B", 10)
            row.cell("Start - End")
            if not parcel_defined:
                row.cell("Parcel")
                row.cell("Parcel Identifier")
                row.cell("Farm")
            row.cell("Dose")
            row.cell("Unit")
            if irrigation_flag:
                row.cell("Irrigation System")
            elif fertilization_flag:
                row.cell("Fertilizer")
                row.cell("Application Method")
            else:
                row.cell("Pesticide")
            pdf.set_font("FreeSerif", "", 9)
            pdf.set_fill_color(255, 255, 240)
            for op in operations:
                # Operation Header
                row = table.row()
                start_time = (
                    op.hasStartDatetime.strftime("%d/%m/%Y")
                    if op.hasStartDatetime
                    else ""
                )
                end_time = (
                    op.hasEndDatetime.strftime("%d/%m/%Y") if op.hasEndDatetime else ""
                )
                row.cell(f"{start_time} - {end_time}")

                if not parcel_defined:
                    parcel_id = op.operatedOn.get("@id") if op.operatedOn else None
                    address = ""
                    farm = ""
                    identifier = ""
                    if parcel_id:
                        parcel = parcel_id.split(":")[3] if op.operatedOn else None
                        if parcel:
                            parcel_data, farm, identifier = get_parcel_info(
                                parcel_id.split(":")[-1],
                                token,
                                geolocator,
                                identifier_flag=True,
                            )
                            address = parcel_data.address

                    row.cell(address)
                    row.cell(identifier)
                    farm_local = (
                        f"Name: {farm.name} | Municipality: {farm.municipality}"
                    )
                    row.cell(farm_local)

                row.cell(
                    f"{op.hasAppliedAmount.numericValue}",
                )
                row.cell(
                    f"{op.hasAppliedAmount.unit}",
                )

                if irrigation_flag:
                    if isinstance(op.usesIrrigationSystem, dict):
                        local_sys = op.usesIrrigationSystem.get("name")
                    else:
                        local_sys = op.usesIrrigationSystem
                    row.cell(local_sys)
                elif fertilization_flag:
                    row.cell("Yes" if op.usesFertilizer else "No")
                    row.cell(op.hasApplicationMethod)
                else:
                    pest = ""
                    if op.usesPesticide:
                        pest = get_pest_from_obj(op, token)
                    row.cell(pest)


    if operations and parcel_defined:
        if irrigation_flag:
            pdf.ln(4)
            area_parcel = (
                int(float(parcel_data.area) / 10_000)
                if float(parcel_data.area) > 0
                else 0
            )
            df_for_calc = prepare_df_for_calculations(operations)
            total_volume_graph = generate_total_volume_graph(df_for_calc, area_parcel)
            pdf.ln(1)
            amount_per_hc_graph = generate_amount_per_hectare(df_for_calc)
            pdf.add_page()
            pdf.set_font("FreeSerif", "B", 15)
            pdf.set_x((pdf.w / 4) - 30)
            pdf.cell(30, 2, "3. Graphs: ", ln=2, align='L')
            pdf.ln(2)
            pdf.set_font("FreeSerif", "", 10)
            pdf.cell(10, 2, "Graph 1: ", ln=2, align='L')
            pdf.ln(2)
            pdf.image(total_volume_graph, type="png", w=180)
            pdf.cell(10, 2, "Graph 2: ", ln=1, align='L')
            pdf.ln(2)
            pdf.image(amount_per_hc_graph, type="png", w=180)

            dict_average_table = generate_aggregation_table_data(df_for_calc)
            pdf.set_fill_color(0, 255, 255)
            pdf.set_font("FreeSerif", "B", 15)
            pdf.add_page()
            pdf.set_x((pdf.w / 4) - 30)
            pdf.cell(30, 2, "4. Aggregates:", align='L', ln=True)
            pdf.ln(4)
            pdf.set_font("FreeSerif", "B", 10)
            with pdf.table(text_align="CENTER") as table:
                row = table.row()
                row.cell("Data")
                row.cell("Per hectare (m3)")
                row.cell("Total volume (m3)")

                pdf.set_font("FreeSerif", "", 9)
                pdf.set_fill_color(255, 255, 240)
                for k, v in dict_average_table.items():
                    row = table.row()
                    row.cell(k)
                    row.cell(f"{v[0]:.2f}")
                    row.cell(f"{v[1]:.2f}")

        elif isinstance(operations[0], CropProtectionOperation):
            pesticide_sums = pesticides_aggregation(operations, token)
            pdf.set_fill_color(0, 255, 255)
            pdf.set_font("FreeSerif", "B", 15)
            pdf.add_page()
            pdf.set_x((pdf.w / 4) - 30)
            pdf.cell(30, 2, "3. Final report:", align='L', ln=True)
            pdf.ln(4)
            pdf.set_font("FreeSerif", "B", 10)
            with pdf.table(text_align="CENTER") as table:
                row = table.row()
                row.cell("Pesticide")
                row.cell("Total")
                pdf.set_font("FreeSerif", "", 9)
                pdf.set_fill_color(255, 255, 240)
                for _, row_df in pesticide_sums.iterrows():
                    row = table.row()
                    row.cell(row_df["Pesticide"])
                    row.cell(f"{row_df['Dose']:.2f} {row_df['Unit']}")

    return pdf


def process_irrigation_fertilization_data(
    data,
    token: dict[str, str],
    pdf_file_name: str,
    from_date: datetime.date = None,
    to_date: datetime.date = None,
    operation_id: str = None,
    parcel_id: str = None,
    irrigation_flag: bool = True,
    fertilization_flag: bool = False,
    pesticides_flag: bool = False,
) -> None:
    """
    Process irrigation data and generate PDF report
    """
    data_used = False
    url_use = "irrigations"

    if fertilization_flag:
        url_use = "fertilization"
    elif pesticides_flag:
        url_use = "pesticides"

    if operation_id:
        json_data = make_get_request(
            url=f"{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS[url_use]}{operation_id}/",
            token=token,
            params={"format": "json"},
        )

        json_data = [json_data] if json_data else None

    else:
        if not data:
            params = {"format": "json"}
            if parcel_id:
                params["parcel"] = parcel_id

            decode_dates_filters(params, from_date, to_date)
            json_data = make_get_request(
                url=f"{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS[url_use]}",
                token=token,
                params=params,
            )

        else:
            data_used = True
            json_data = json.loads(data)
            if json_data:
                json_data = json_data["@graph"]

    if json_data:
        operations = parse_irrig_fert_operations(
            json_data,
            irrigation_flag=irrigation_flag,
            fertilization_flag=fertilization_flag,
        )
    else:
        operations = []

    try:
        pdf = create_pdf_from_operations(
            operations,
            token,
            data_used,
            parcel_id=parcel_id,
            from_date=from_date,
            to_date=to_date,
            irrigation_flag=irrigation_flag,
            fertilization_flag=fertilization_flag,
        )
    except Exception:
        raise HTTPException(
            status_code=400, detail="PDF generation of irrigation report failed."
        )
    pdf_dir = f"{settings.PDF_DIRECTORY}{pdf_file_name}"
    os.makedirs(os.path.dirname(f"{pdf_dir}.pdf"), exist_ok=True)
    pdf.output(f"{pdf_dir}.pdf")
