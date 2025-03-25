from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AnimalGroup(BaseModel):
    hasName: str


class HasAgriParcel(BaseModel):
    id: str = Field(alias="@id")


class Animal(BaseModel):
    id: str = Field(alias="@id")
    nationalID: str
    name: str
    description: str
    hasAgriParcel: Optional[HasAgriParcel] = None
    sex: int
    castrated: bool
    species: str
    breed: str
    birthdate: datetime
    isMemberOfAnimalGroup: Optional[AnimalGroup]
    status: int
    invalidatedAtTime: Optional[datetime] = None
    dateCreated: Optional[datetime] = None
    dateModified: Optional[datetime] = None
