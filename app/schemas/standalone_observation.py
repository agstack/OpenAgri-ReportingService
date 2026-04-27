from typing import Optional

from pydantic import BaseModel


class ManualParcelInfo(BaseModel):
    address: str = ""
    identifier: str = ""
    area: float = 0.0
    lat: Optional[float] = None
    lng: Optional[float] = None


class ManualFarmInfo(BaseModel):
    name: str = ""
    municipality: str = ""
    administrator: str = ""
    vatID: str = ""
    contactPerson: str = ""
    description: str = ""
