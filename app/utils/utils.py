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
        logger.info("Error with geolocator", e)
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

