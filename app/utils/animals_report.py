import json
import os
from typing import List, Union

from fastapi import HTTPException

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
    pdf.add_page()
    add_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_title("Animal Report")
    pdf.ln()

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "Animal Report")
    pdf.ln(10)

    for animal in animals:
        pdf.set_font("FreeSerif", "B", 9)
        pdf.cell(
            0, 10, f"Animal: {animal.name} (ID: {animal.id.split(':')[3]})", ln=True
        )
        pdf.set_font("FreeSerif", "", 9)
        pdf.cell(0, 10, f"National ID: {animal.nationalID}", ln=True)
        pdf.cell(0, 10, f"Description: {animal.description}", ln=True)
        pdf.cell(
            0,
            10,
            f"Agricultural Parcel: {animal.hasAgriParcel.id.split(':')[3] if animal.hasAgriParcel else ''}",
            ln=True,
        )
        pdf.cell(0, 10, f"Species: {animal.species} | Breed: {animal.breed}", ln=True)
        pdf.cell(
            0,
            10,
            f"Sex: {'Male' if animal.sex == 0 else 'Female'} | Castrated: {animal.isCastrated}",
            ln=True,
        )
        pdf.cell(0, 10, f"Birthdate: {animal.birthdate}", ln=True)
        pdf.cell(0, 10, f"Status: {animal.status}", ln=True)

        if animal.invalidatedAtTime:
            pdf.cell(0, 10, f"Invalidated At: {animal.invalidatedAtTime}", ln=True)

        if animal.isMemberOfAnimalGroup:
            pdf.cell(
                0, 10, f"Animal group: {animal.isMemberOfAnimalGroup.hasName}", ln=True
            )

        pdf.cell(
            0,
            10,
            f"Created: {animal.dateCreated if animal.dateCreated else 'N/A'} | Modified: {animal.dateModified if animal.dateModified else 'N/A'}",
            ln=True,
        )
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
