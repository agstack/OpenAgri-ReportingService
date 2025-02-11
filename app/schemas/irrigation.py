from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class QuantityValue(BaseModel):
    """Model for quantity measurements"""

    unit: str
    numericValue: float


class IrrigationOperation(BaseModel):
    """Model for irrigation operations"""

    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    activityType: str
    title: str
    details: str
    hasStartDatetime: datetime
    hasEndDatetime: datetime
    responsibleAgent: str
    usesAgriculturalMachinery: List[str]
    hasAppliedAmount: QuantityValue
    usesIrrigationSystem: str
    operatedOn: str
