from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class PDF(BaseModel):
    uuid: str


class QualityCertification(BaseModel):
    cert_type: Optional[str] = None
    cert_number: Optional[str] = None
    cert_issuing_body: Optional[str] = None
    cert_issue_date: Optional[str] = None
    cert_expiry_date: Optional[str] = None
    cert_notes: Optional[str] = None
