import json
import os
from typing import List, Union

from fastapi import HTTPException
from fpdf.fonts import FontFace

from core import settings
from utils import EX, add_fonts, decode_jwt_token
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
    pdf.add_page()
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_title("Animal Report")
    pdf.ln()

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "Animal Report")
    pdf.ln(10)
    style = FontFace(fill_color=(180, 196, 36))
    if animals:
        with pdf.table(text_align="CENTER", padding=0.5) as table:
            row = table.row()
            row.style = style
            pdf.set_font("FreeSerif", "B", 10)
            row.cell("Animal"); row.cell("National ID"); row.cell("Description"); row.cell("Parcel ID")
            row.cell("Species"); row.cell("Sex"); row.cell("Birthdate"); row.cell("Status")
            row.cell("Invalidated"); row.cell("Is Member of group");  row.cell("Created")
            row.cell("RModified")
            style = FontFace(fill_color=(255, 255, 240	))
            pdf.set_font("FreeSerif", "B", 9)
            for animal in animals:
                row = table.row()
                row.style = style
                row.cell(animal.name); row.cell(animal.nationalID); row.cell(animal.description)
                row.cell(
                    f"{animal.hasAgriParcel.id.split(':')[3] if animal.hasAgriParcel else ''}",
                )
                row.cell(animal.species)
                row.cell(
                    f"{'Male' if animal.sex == 0 else 'Female'} | Castrated: {animal.isCastrated}",
                )
                row.cell(animal.birthdate); row.cell(animal.status)
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
    token: dict[str, str], pdf_file_name: str, params: dict | None = None, data=None
) -> None:
    """
    Process animal data and generate PDF report
    """
    if params:
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
