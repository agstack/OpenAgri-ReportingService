import json
from typing import Optional

import requests
from fastapi import HTTPException

import utils.utils
from core import settings
from utils.irrigation_report import (
    create_pdf_from_aggregations,
    parse_irr_jsonld_to_schema,
)


class ReportHandler:
    """
    Report Handler will be used for generating PDF reports

    """

    def __init__(self, *, file, file_type, dataset_id: Optional[str] = None):
        """
        :param file: Report model file (if exist)
        :param file_type: Report model type


        """
        self.file = file
        self.file_type = file_type

        self.handlers = {
            "work-book": (
                lambda json_file: utils.work_book(
                    farm=utils.parse_farm_profile(json_file),
                    plot=utils.parse_plot_detail(json_file),
                    cult=utils.parse_generic_cultivation_info(json_file),
                    irri=create_pdf_from_aggregations(
                        parse_irr_jsonld_to_schema(json_file)
                    ),
                    fert=utils.parse_fertilization(json_file),
                    pdmd=utils.parse_plant_protection(json_file),
                ),
                "",
            ),
            "plant-protection": (
                lambda json_file: utils.plant_protection(
                    utils.parse_plant_protection(json_file)
                ),
                "api/plan/",
            ),
            "irrigations": (
                lambda json_file: create_pdf_from_aggregations(
                    parse_irr_jsonld_to_schema(json_file)
                ),
                f"irr_backend/api/v1/dataset/{dataset_id}/analysis",
            ),
            "fertilisations": (
                lambda json_file: utils.fertilisation(
                    utils.parse_fertilization(json_file)
                ),
                "api/fertilisations",
            ),
            "livestock": (
                lambda json_file: utils.livestock(utils.parse_livestock(json_file)),
                "api/livestock",
            ),
            "compost": (
                lambda json_file: utils.generate_weather_report(
                    utils.parse_weather_jsonld(json_file)
                ),
                "api/compost",
            ),
            "harvests": (lambda: utils.harvests(), ""),
        }

    def generate_pdf(self, token=None) -> Optional[utils.EX]:
        try:
            if not settings.USING_GATEKEEPER or self.file:
                json_file = None
                if self.file_type != "harvests":
                    json_file = json.loads(self.file)
                handler = self.handlers.get(self.file_type, "work-book")
                return_value = (
                    handler[0](json_file)
                    if self.file_type != "harvests"
                    else handler[0]()
                )
                return return_value
            else:
                handler = self.handlers.get(self.file_type, "work-book")

                json_ld_response = requests.get(
                    url=settings.GATEKEEPER_BASE_URL.unicode_string() + handler[1],
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer {}".format(token),
                    },
                )

                if json_ld_response.status_code != 200:
                    raise HTTPException(
                        status_code=400,
                        detail="Gatekeeper returned status code: {}".format(
                            json_ld_response.status_code
                        ),
                    )

                json_ld_response = json_ld_response.json()

                return_value = (
                    handler[0](json.loads(json_ld_response))
                    if self.file_type != "harvests"
                    else handler[0]()
                )

                return return_value
        except Exception as e:
            print(e)
            return None
