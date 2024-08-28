import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    name: str
    file: str
    type: str


class ReportUpdate(BaseModel):
    name: str


class ReportDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ReportDBID(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int


class FarmProfile(BaseModel):
    name: Optional[str]
    father_name: Optional[str]
    vat: Optional[str]
    head_office_details: Optional[str]
    phone: Optional[str]
    district: Optional[str]
    county: Optional[str]
    municipality: Optional[str]
    community: Optional[str]
    place_name: Optional[str]
    farm_area: Optional[str]
    plot_ids: Optional[List[int]]


class MachineryAssetsOfFarm(BaseModel):
    index: Optional[int]
    description: Optional[str]
    serial_number: Optional[str]
    date_of_manufacturing: Optional[datetime.date]


class PlotParcelDetail(BaseModel):
    plot_id: Optional[int]
    reporting_year: Optional[int]
    cartographic: Optional[str]
    region: Optional[str]
    toponym: Optional[str]
    area: Optional[str]
    nitro_area: Optional[bool]
    natura_area: Optional[bool]
    pdo_pgi_area: Optional[bool]
    irrigated: Optional[bool]
    cultivation_in_levels: Optional[bool]
    ground_slope: Optional[bool]
    # photo: Optional[bytes]


class GenericCultivationInformationForParcel(BaseModel):
    cultivation_type: Optional[str]
    variety: Optional[str]
    irrigated: Optional[bool]
    greenhouse: Optional[bool]
    production_direction: Optional[str]
    planting_system: Optional[str]
    planting_distances_of_lines: Optional[int]
    planting_distance_between_lines: Optional[int]
    number_of_productive_trees: Optional[int]


class Harvest(BaseModel):
    date: Optional[datetime.date]
    production_amount: Optional[float]
    unit: Optional[str]


class Irrigation(BaseModel):
    started_date: Optional[datetime.datetime]
    ended_date: Optional[datetime.datetime]
    dose: Optional[int]
    unit: Optional[str]
    watering_system: Optional[str]


class PestManagement(BaseModel):
    date: Optional[datetime.date]
    enemy_target: Optional[str]
    active_substance: Optional[str]
    product: Optional[str]
    dose: Optional[float]
    unit: Optional[str]
    area: Optional[str]
    treatment_description: Optional[str]


# class Fertilization(BaseModel):
#     date: Optional[datetime.date]
#     product: Optional[str]
#     quantity: Optional[float]
#     unit: Optional[str]
#     treatment_plan: Optional[str]
#     form_of_treatment: Optional[str]
#     operation_type: Optional[str]
#     treatment_description: Optional[str]
#
#
# class GrowthStages(BaseModel):
#     date: Optional[datetime.date]
#     product: Optional[str]
#     quantity: Optional[float]
#     unit: Optional[str]
#     treatment_plan: Optional[str]
#     form_of_treatment: Optional[str]
#     operation_type: Optional[str]
