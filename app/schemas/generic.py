from pydantic import BaseModel


class Message(BaseModel):
    message: str


class PDF(BaseModel):
    uuid: str
