import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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
    depiction: Optional[str]


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


class Fertilization(BaseModel):
    date: Optional[datetime.date]
    product: Optional[str]
    quantity: Optional[float]
    unit: Optional[str]
    treatment_plan: Optional[str]
    form_of_treatment: Optional[str]
    operation_type: Optional[str]
    treatment_description: Optional[str]


class Livestock(BaseModel):
    id: str | int
    name: Optional[str]
    type: Optional[str]
    category: Optional[str]
    breed: Optional[str]
    color: Optional[str]
    gender: Optional[str]
    birth_date: Optional[datetime.date]
    is_dam_owned: Optional[bool]
    sire_id: Optional[str]
    is_sire_owned: Optional[bool]
    loss_cause: Optional[str]
    loss_date: Optional[datetime.date]
    sold_through: Optional[str]
    sale_amount: Optional[float]
    sale_weight: Optional[float]
    is_owned: Optional[bool]


class WeatherObservation(BaseModel):
    timestamp: Optional[str] = Field(
        None, description="The timestamp of the weather observation in ISO 8601 format."
    )
    wind_speed: Optional[float] = Field(
        None, description="Observed wind speed in meters per second."
    )
    air_pressure: Optional[float] = Field(
        None, description="Observed air pressure in pascals."
    )
    humidity: Optional[float] = Field(None, description="Specific humidity percentage.")
    temperature: Optional[float] = Field(
        None, description="Air temperature in degrees Celsius."
    )


# class GrowthStages(BaseModel):
#     date: Optional[datetime.date]
#     product: Optional[str]
#     quantity: Optional[float]
#     unit: Optional[str]
#     treatment_plan: Optional[str]
#     form_of_treatment: Optional[str]
#     operation_type: Optional[str]
