import datetime
import logging
import os

import jwt
from fpdf import FPDF
from pydantic import BaseModel

from core import settings
from utils.json_handler import make_get_request
from geopy.geocoders import Nominatim

logger = logging.Logger("utils")


def add_fonts(pdf):
    fonts_folder_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fonts"
    )

    pdf.add_font(
        "FreeSerif", "", os.path.join(fonts_folder_path, "FreeSerif.ttf"), uni=True
    )
    pdf.add_font(
        "FreeSerif", "B", os.path.join(fonts_folder_path, "FreeSerifBold.ttf"), uni=True
    )


class EX(FPDF):
    def header(self):
        self.image(
            "https://horizon-openagri.eu/wp-content/uploads/2023/12/Logo-Open-Agri-blue-1024x338.png",
            w=40.0,
            keep_aspect_ratio=True,
            x=160,
        )

    def footer(self):
        self.set_y(-15)
        self.set_font("FreeSerif", "", 7)
        acknowledgement_text = """
            \tOpenAgri has received funding from the EU's Horizon Europe research and  innovation programme under Grant Agreement no. 101134083. This output reflects
            only the author's view and the European Commission cannot be held responsible for any use that may be made of the information contained therein.
        """
        image_path = os.path.join(settings.PROJECT_ROOT, "assets", "eu.png")
        self.image(image_path, x=self.x, y=self.y, w=20)
        self.set_x(self.get_x()+10)
        self.multi_cell(200, 2, acknowledgement_text, border=0, align="J")


def decode_jwt_token(token: str) -> dict:
    """
    Decode JWT token

    :param token: JWT token (str)

    :return: Dictionary with decoded information
    """
    decoded = jwt.decode(token, options={"verify_signature": False})
    return decoded


def decode_dates_filters(
    params: dict, from_date: datetime.date = None, to_date: datetime.date = None
):
    try:
        if from_date:
            from_date = from_date.strftime("%Y-%m-%d")
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.info(
            f"Error in parsing date: {e}. Request will be sent without date filters."
        )


class FarmInfo(BaseModel):
    description: str
    administrator: str
    vatID: str
    name: str
    municipality: str
    contactPerson: str


class ParcelInfo(BaseModel):
    address: str
    area: float
    lat: float | None = 0
    long: float | None = 0


def get_parcel_info(
    parcel_id: str, token: dict, geolocator: Nominatim, identifier_flag: bool = False
):
    farm = FarmInfo(
        description="",
        administrator="",
        vatID="",
        name="",
        municipality="",
        contactPerson="",
    )
    parcel_info = ParcelInfo(address="", area=0.0, lat=0.0, long=0.0)
    identifier = ""
    if not settings.REPORTING_USING_GATEKEEPER:
        if identifier_flag:
            return parcel_info, farm, identifier
        else:
            return parcel_info, farm
    farm_parcel_info = make_get_request(
        url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["parcel"]}{parcel_id}/',
        token=token,
        params={"format": "json"},
    )

    if not farm_parcel_info:
        if identifier_flag:
            return parcel_info, farm, identifier
        else:
            return parcel_info, farm

    location = farm_parcel_info.get("location")
    parcel_info.area = farm_parcel_info.get("area", 0.0)
    farm_id = farm_parcel_info.get("farm").get("@id", None)

    if farm_id:
        farm_id = farm_id.split(":")[-1]
    if farm_id:
        farm_info = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["farm"]}{farm_id}/',
            token=token,
            params={"format": "json"},
        )

        contact = farm_info.get("contactPerson", {})
        farm = FarmInfo(
            description=farm_info.get("description", ""),
            administrator=farm_info.get("administrator", ""),
            vatID=farm_info.get("vatID", ""),
            name=farm_info.get("name", ""),
            municipality=farm_info.get("address", {}).get("municipality", ""),
            contactPerson=f"{contact.get('firstname', '')} {contact.get('lastname', '')}",
        )

    try:
        identifier = farm_parcel_info.get("identifier")
        if location:
            lat = location.get('lat')
            long = location.get('long')
            coordinates = f"{lat}, {long}"
            parcel_info.lat = lat
            parcel_info.long = long
            l_info = geolocator.reverse(coordinates)
            address_details = l_info.raw.get("address", {})
            city = address_details.get("city", "")
            country = address_details.get("country")
            postcode = address_details.get("postcode")
            address = f"Country: {country} | City: {city} | Postcode: {postcode}"
            parcel_info.address = address
    except Exception as e:
        logger.error("Error with geolocator", e)
        if identifier_flag:
            return parcel_info, farm, identifier
        return parcel_info, farm

    if identifier_flag:
        return parcel_info, farm, identifier
    return parcel_info, farm


def get_farm_operation_data(
    id: str, token: dict[str, str], params: dict, observations: list, materials: list
):
    """
    Fetches observations and material-related data for a farm operation.

    """
    base_url = settings.REPORTING_FARMCALENDAR_BASE_URL
    urls = settings.REPORTING_FARMCALENDAR_URLS

    # Fetch and append observations
    obs_url = f'{base_url}{urls["operations"]}{id}{urls["observations"]}'
    observations_local = make_get_request(url=obs_url, token=token, params=params)
    if observations_local:
        observations.extend(observations_local)

    # Fetch and append materials
    material_url = f'{base_url}{urls["operations"]}{id}{urls["materials"]}'
    materials_partials = make_get_request(url=material_url, token=token, params=params)
    if materials_partials:
        materials.extend(materials_partials)

    # Fetch and append irrigation operations
    irrigation_url = f'{base_url}{urls["operations"]}{id}{urls["irrigations"]}'
    irrigation_ops = make_get_request(url=irrigation_url, token=token, params=params)
    if irrigation_ops:
        materials.extend(irrigation_ops)

    # Fetch and append compost turning operations
    turn_url = f'{base_url}{urls["operations"]}{id}{urls["turning_operations"]}'
    compost_turning_ops = make_get_request(url=turn_url, token=token, params=params)
    if compost_turning_ops:
        materials.extend(compost_turning_ops)


def get_pesticide(id: str, token: dict[str, str]):
    """
    Fetches pesticide for Crop Operation

    """
    base_url = settings.REPORTING_FARMCALENDAR_BASE_URL
    urls = settings.REPORTING_FARMCALENDAR_URLS

    pest_url = f'{base_url}{urls["pest"]}{id}/'
    pest = make_get_request(url=pest_url, token=token, params={"format": "json"})
    return pest


def display_pdf_parcel_details(pdf: FPDF, parcel_id: str, geolocator: Nominatim, token: str | dict) -> ParcelInfo:
    parcel_data, farm, identifier = get_parcel_info(
        parcel_id, token, geolocator, identifier_flag=True
    )
    address = parcel_data.address

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
    pdf.multi_cell(0, 8, farm.description, fill=True)
    return parcel_data


