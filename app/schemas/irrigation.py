from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class QuantityValue(BaseModel):
    """Model for quantity measurements"""

    unit: str
    numericValue: float


class IrrigationOperation(BaseModel):
    """Model for irrigation operations"""

    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    activityType: dict
    title: Optional[str] = ""
    details: Optional[str] = ""
    hasStartDatetime: Optional[datetime] = None
    hasEndDatetime: Optional[datetime] = None
    responsibleAgent: Optional[str] = None
    usesAgriculturalMachinery: List[dict] = []
    hasAppliedAmount: QuantityValue
    usesIrrigationSystem: str
    operatedOn: Optional[dict] = None
