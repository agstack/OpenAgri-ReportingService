from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CropObservation(BaseModel):
    """Model for observations"""

    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    activityType: dict
    title: str
    details: str
    hasStartDatetime: Optional[datetime] = None
    hasEndDatetime: Optional[datetime] = None
    responsibleAgent: Optional[str] = None
    usesAgriculturalMachinery: List[dict] = []
    hasValue: str
    isMeasuredIn: str
    relatesToProperty: str


class Operation(BaseModel):
    """Model for farm operations"""

    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    activityType: dict
    title: str
    details: str
    hasStartDatetime: Optional[datetime] = None
    hasEndDatetime: Optional[datetime] = None
    responsibleAgent: Optional[str] = None
    usesAgriculturalMachinery: List[dict] = []
