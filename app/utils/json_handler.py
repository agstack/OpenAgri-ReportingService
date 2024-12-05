import json
from typing import Optional

import utils.utils
from models import Report


class ReportHandler:
    """
    Report Handler will be used for generating PDF reports

    """

    def __init__(self, *, report_db: Report):
        """
        :param report_db: Report model data

        """
        self.report_db = report_db
        self.file_type = report_db.type

        self.handlers = {
            "work-book": lambda json_file: utils.work_book(
                farm=utils.parse_farm_profile(json_file),
                plot=utils.parse_plot_detail(json_file),
                cult=utils.parse_generic_cultivation_info(json_file),
                irri=utils.parse_irrigation(json_file),
                fert=utils.parse_fertilization(json_file),
                pdmd=utils.parse_plant_protection(json_file),
            ),
            "plant-protection": lambda json_file: utils.plant_protection(
                utils.parse_plant_protection(json_file)
            ),
            "irrigations": lambda json_file: utils.irrigations(
                utils.parse_irrigation(json_file)
            ),
            "fertilisations": lambda json_file: utils.fertilisation(
                utils.parse_fertilization(json_file)
            ),
            "livestock": lambda json_file: utils.livestock(
                utils.parse_livestock(json_file)
            ),
            "harvests": lambda _: utils.harvests(),
        }

    def generate_pdf(self) -> Optional[utils.EX]:
        try:
            json_file = None
            if self.file_type != "harvests":
                json_file = json.loads(self.report_db.file)
            handler = self.handlers.get(self.file_type, "work-book")
            return_value = (
                handler(json_file) if self.file_type != "harvests" else handler()
            )
            return return_value
        except Exception:
            return None
