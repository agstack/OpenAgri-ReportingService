from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AnimalGroup(BaseModel):
    hasName: Optional[str] = None


class HasAgriParcel(BaseModel):
    id: str = Field(alias="@id")


class Animal(BaseModel):
    id: str = Field(alias="@id")
    nationalID: Optional[str] = None
    name: Optional[str] = ""
    description: Optional[str] = ""
    hasAgriParcel: Optional[HasAgriParcel] = None
    sex: int
    isCastrated: bool = False
    species: str
    breed: Optional[str] = None
    birthdate: datetime
    isMemberOfAnimalGroup: Optional[AnimalGroup] = None
    status: int
    invalidatedAtTime: Optional[datetime] = None
    dateCreated: Optional[datetime] = None
    dateModified: Optional[datetime] = None
