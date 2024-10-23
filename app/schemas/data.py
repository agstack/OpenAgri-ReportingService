from pydantic import BaseModel, ConfigDict


class DataCreate(BaseModel):
    filename: str
    data: str


class DataUpdate(BaseModel):
    filename: str


class DataDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # id: int
    data: str


class DataID(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int


class DataUpload(DataUpdate):
    pass
