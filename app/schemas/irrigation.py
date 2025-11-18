from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class QuantityValue(BaseModel):
    """Model for quantity measurements"""

    unit: str
    numericValue: float

class GenericModel(BaseModel):
    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    activityType: Optional[dict] = None
    title: Optional[str] = ""
    details: Optional[str] = ""
    hasStartDatetime: Optional[datetime] = None
    hasEndDatetime: Optional[datetime] = None
    responsibleAgent: Optional[str] = None
    usesAgriculturalMachinery: List[dict] = []
    hasAppliedAmount: QuantityValue

class IrrigationOperation(GenericModel):
    """Model for irrigation operations"""
    usesIrrigationSystem: Optional[Union[str, dict]] = None
    operatedOn: Optional[dict] = None

class FertilizationOperation(IrrigationOperation):
    hasApplicationMethod: Optional[str] = None
    usesFertilizer: Optional[dict] = None

class CropProtectionOperation(GenericModel):
    operatedOn: Optional[dict] = None
    usesPesticide: Optional[dict] = None
