import datetime
import logging
import os

import jwt
from fpdf import FPDF

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
            params['from_date'] = from_date
        if to_date:
            params['to_date'] = to_date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.info(f"Error in parsing date: {e}. Request will be sent without date filters.")