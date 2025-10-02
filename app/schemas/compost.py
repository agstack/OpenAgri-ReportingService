from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QuantityValue(BaseModel):
    type: str = Field(alias="@type")
    unit: str = ""
    numericValue: float = 0.0

class QuantityValueIrrigation(BaseModel):
    unit: str = ""
    numericValue: float = 0.0

class CompostMaterial(BaseModel):
    type: str = Field(alias="@type")
    typeName: str = ""
    quantityValue: Optional[QuantityValue] = None


class ActivityType(BaseModel):
    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    category: Optional[str] = None


class HasResult(BaseModel):
    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    unit: Optional[str] = None
    hasValue: Optional[str] = None

class CropObservation(BaseModel):
    """Model for observations"""

    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    activityType: Optional[dict] = None
    title: Optional[str] = ""
    details: Optional[str] = ""
    hasStartDatetime: Optional[datetime] = None
    hasEndDatetime: Optional[datetime] = None
    phenomenonTime: Optional[datetime] = None
    responsibleAgent: Optional[str] = None
    usesAgriculturalMachinery: List[dict] = []
    hasResult: Optional[HasResult] = None
    isMeasuredIn: Optional[str] = None
    observedProperty: Optional[str] = None

class Operation(BaseModel):
    """Model for farm operations"""

    type: str = Field(alias="@type")
    id: str = Field(alias="@id")
    activityType: Optional[dict] = {}
    title: str = ""
    details: str = ""
    hasStartDatetime: Optional[datetime] = None
    hasEndDatetime: Optional[datetime] = None
    responsibleAgent: Optional[str] = ""
    usesAgriculturalMachinery: List[dict] = []
    isOperatedOn: Optional[dict] = None
    operatedOn: Optional[dict] = {}
    hasMeasurement: list[dict] = None
    hasNestedOperation: list[dict] = None
    usesIrrigationSystem: Optional[str] = None
    hasAgriParcel: Optional[dict] = None


class AddRawMaterialOperation(Operation):
    usesAgriculturalMachinery: List = []
    hasCompostMaterial: List[CompostMaterial] = []
    hasAppliedAmount: Optional[QuantityValueIrrigation] = None