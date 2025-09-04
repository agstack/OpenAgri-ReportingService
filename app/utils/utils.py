import datetime
import logging
import os

import jwt
from fpdf import FPDF

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


def decode_jwt_token(token: str) -> dict:
    """
    Decode JWT token

    :param token: JWT token (str)

    :return: Dictionary with decoded information
    """
    decoded = jwt.decode(token, options={"verify_signature": False})
    return decoded

def decode_dates_filters(params: dict, from_date: datetime.date =  None, to_date: datetime.date = None):
    try:
        if from_date:
            from_date = from_date.strftime("%Y-%m-%d")
            params['fromDate'] = from_date
        if to_date:
            params['toDate'] = to_date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.info(f"Error in parsing date: {e}. Request will be sent without date filters.")


def get_parcel_info(parcel_id: str, token: dict, geolocator: Nominatim):
    farm_parcel_info = make_get_request(
        url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["parcel"]}{parcel_id}/',
        token=token,
        params={"format": "json"}
    )
    location = farm_parcel_info.get("location")
    address = ''
    farm = ''
    try:
        if location:
            coordinates = f"{location.get('lat')}, {location.get('long')}"
            l_info = geolocator.reverse(coordinates)
            address_details = l_info.raw.get('address', {})
            city = address_details.get('city')
            country = address_details.get("country")
            postcode = address_details.get('postcode')
            address = f"Country: {country} | City: {city} | Postcode: {postcode}"
    except Exception as e:
        logger.error("Error with geolocator", e)
        return address, farm

    farm_id = farm_parcel_info.get("farm").get("@id", None)
    if farm_id:
        farm_id = farm_id.split(":")[-1]
    if farm_id:
        farm_info = make_get_request(
            url=f'{settings.REPORTING_FARMCALENDAR_BASE_URL}{settings.REPORTING_FARMCALENDAR_URLS["farm"]}{farm_id}/',
            token=token,
            params={"format": "json"}
        )

        farm = f"Name: {farm_info.get('name', '')} | Municipality: {farm_info.get('address',{}).get('municipality', '')}"
    return address, farm


def get_farm_operation_data(id: str, token: dict[str, str], params: dict, observations: list, materials: list):
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
