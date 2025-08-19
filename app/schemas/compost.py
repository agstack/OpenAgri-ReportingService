from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QuantityValue(BaseModel):
    type_: str = Field(alias="@type")
    unit: str = ""
    numericValue: float = 0.0


class CompostMaterial(BaseModel):
    type_: str = Field(alias="@type")
    typeName: str = ""
    quantityValue: Optional[QuantityValue] = None


class ActivityType(BaseModel):
    type_: str = Field(alias="@type")
    id_: str = Field(alias="@id")


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
    phenomenonTime: Optional[datetime] = None
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
    title: str = ""
    details: str = ""
    hasStartDatetime: Optional[datetime] = None
    hasEndDatetime: Optional[datetime] = None
    responsibleAgent: Optional[str] = None
    usesAgriculturalMachinery: List[dict] = []
    isOperatedOn: dict = None
    hasMeasurement: list[dict] = None
    hasNestedOperation: list[dict] = None


class AddRawMaterialOperation(Operation):
    usesAgriculturalMachinery: List = []
    hasCompostMaterial: List[CompostMaterial] = []