from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class HasResult(BaseModel):
    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    unit: Optional[str] = (None,)
    hasValue: Optional[str] = None


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
    hasResult: Optional[HasResult] = None
    isMeasuredIn: Optional[str] = None
    relatesToProperty: Optional[str] = None
    observedProperty: Optional[str] = None


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
