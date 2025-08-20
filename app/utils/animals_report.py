import json
import os
from typing import List, Union

from fastapi import HTTPException
from fpdf.fonts import FontFace

from core import settings
from utils import EX, add_fonts, decode_jwt_token, decode_dates_filters
from schemas.animals import *
from utils.json_handler import make_get_request


def parse_animal_data(data: Union[List[dict], str]) -> Optional[List[Animal]]:
    """
    Parse list of animal records from JSON data
    """
    try:
        return [Animal.model_validate(item) for item in data]
    except Exception as e:
        print(f"Error parsing animal data: {e}")
        return None


def create_pdf_from_animals(animals: List[Animal]):
    """
    Create PDF report from animal records
    """
    pdf = EX()
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    EX.ln(pdf)

    pdf.set_font("FreeSerif", "B", 14)
    pdf.cell(0, 10, "Animal Data Report", ln=True, align="C")
    pdf.set_font("FreeSerif", style="", size=9)
    pdf.cell(0, 7, "Farm Calendar  Report", ln=True, align="C")
    pdf.ln(5)

    y_position = pdf.get_y()
    line_end_x = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.line(pdf.l_margin, y_position, line_end_x, y_position)
    pdf.ln(5)
    pdf.set_fill_color(0, 255, 255)
    if animals:
        with pdf.table(text_align="CENTER", padding=0.5) as table:
            row = table.row()
            pdf.set_font("FreeSerif", "B", 10)
            row.cell("Animal")
            row.cell("National ID") row.cell("Description") row.cell("Parcel ID")
            row.cell("Species") row.cell("Sex") row.cell("Birthdate") row.cell("Status")
            row.cell("Invalidated") row.cell("Is Member of group")  row.cell("Created")
            row.cell("RModified")
            pdf.set_fill_color(255, 255, 240)
            pdf.set_font("FreeSerif", "B", 9)
            for animal in animals:
                row = table.row()
                row.cell(animal.name) row.cell(animal.nationalID) row.cell(animal.description)
                row.cell(
                    f"{animal.hasAgriParcel.id.split(':')[3] if animal.hasAgriParcel else ''}",
                )
                row.cell(animal.species)
                row.cell(
                    f"{'Male' if animal.sex == 0 else 'Female'} | Castrated: {animal.isCastrated}",
                )
                row.cell(animal.birthdate) row.cell(animal.status)
                row.cell(f"{animal.invalidatedAtTime if animal.invalidatedAtTime else 'N/A'}")
                row.cell(f"{animal.isMemberOfAnimalGroup.hasName if animal.isMemberOfAnimalGroup else 'N/A'}"
                )
                row.cell(
                    f"Created: {animal.dateCreated if animal.dateCreated else 'N/A'}",
                )
                row.cell(f"{animal.dateModified if animal.dateModified else 'N/A'}")
                pdf.ln(10)

    return pdf


def process_animal_data(
        token: dict[str, str], pdf_file_name: str, params: dict | None = None, data=None,
        from_date: datetime.date = None,
        to_date: datetime.date = None
) -> None:
    """
    Process animal data and generate PDF report
    """
    if params:
        decode_dates_filters(params, from_date, to_date)
        json_data = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["animals"]}',
            token=token,
            params=params,
        )

    else:
        json_data = json.load(data.file)

    animals = parse_animal_data(json_data)

    try:
        anima_pdf = create_pdf_from_animals(animals)
    except Exception:
        raise HTTPException(
            status_code=400, detail="PDF generation of animal report failed."
        )
    pdf_dir = f"{settings.PDF_DIRECTORY}{pdf_file_name}"
    os.makedirs(os.path.dirname(f"{pdf_dir}.pdf"), exist_ok=True)
    anima_pdf.output(f"{pdf_dir}.pdf")
