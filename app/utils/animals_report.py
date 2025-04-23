from typing import List, Union
from utils import EX, add_fonts
from schemas.animals import *


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
            f"Sex: {'Male' if animal.sex == 0 else 'Female'} | Castrated: {animal.castrated}",
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


def process_animal_data(json_data: Union[List[dict], str], pdf_file_name: str):
    """
    Process animal data and generate PDF report
    """
    animals = parse_animal_data(json_data)
    if not animals:
        return None
    anima_pdf = create_pdf_from_animals(animals)
    anima_pdf.output(f"{pdf_file_name}.pdf")
