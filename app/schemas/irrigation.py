from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class Measure(BaseModel):
    hasNumericValue: float
    hasUnit: str


class QuantityValue(BaseModel):
    numericValue: float
    unit: str
    atDepth: Measure


class SaturationAnalysis(BaseModel):
    numberOfSaturationDays: int
    hasSaturationDates: List[datetime]
    hasFieldCapacities: List[QuantityValue]


class StressAnalysis(BaseModel):
    numberOfStressDays: int
    hasStressDates: List[datetime]
    hasStressLevels: List[QuantityValue]


class IrrigationAnalysis(BaseModel):
    numberOfIrrigationOperations: int
    numberOfHighDoseIrrigationOperations: int
    hasHighDoseIrrigationOperationDates: List[datetime]


class Instant(BaseModel):
    inXSDDateTime: datetime


class Interval(BaseModel):
    hasBeginning: Instant
    hasEnd: Instant


class SoilMoistureAggregation(BaseModel):
    description: str
    duringPeriod: Interval
    numberOfPrecipitationEvents: int
    saturationAnalysis: SaturationAnalysis
    stressAnalysis: StressAnalysis
    irrigationAnalysis: IrrigationAnalysis
