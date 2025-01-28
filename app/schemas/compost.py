from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class CropObservation(BaseModel):
    """Model for observations"""

    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    activityType: str
    title: str
    details: str
    hasStartDatetime: datetime
    hasEndDatetime: datetime
    responsibleAgent: str
    usesAgriculturalMachinery: List[str]
    hasValue: str
    isMeasuredIn: str
    relatesToProperty: str


class Operation(BaseModel):
    """Model for farm operations"""

    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    activityType: str
    title: str
    details: str
    hasStartDatetime: datetime
    hasEndDatetime: datetime
    responsibleAgent: str
    usesAgriculturalMachinery: List[str]
