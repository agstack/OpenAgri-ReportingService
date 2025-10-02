from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class QuantityValue(BaseModel):
    """Model for quantity measurements"""

    unit: str
    numericValue: float


class IrrigationOperation(BaseModel):
    """Model for irrigation operations"""

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
    usesIrrigationSystem: Optional[Union[str, dict]] = None
    operatedOn: Optional[dict] = None
