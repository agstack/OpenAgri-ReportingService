import os

import jwt
from fpdf import FPDF


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
