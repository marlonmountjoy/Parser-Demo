from datetime import datetime
from pydantic import BaseModel, Field


class EmailIn(BaseModel):
    sender: str = Field(..., examples=["supplier@example.com"])
    subject: str
    body: str
    received_at: datetime | None = None


class ParsedEmailOut(BaseModel):
    id: int
    sender: str
    subject: str
    category: str
    confidence: float
    extracted: dict
    created_at: datetime


class ActionItemOut(BaseModel):
    id: int
    parsed_email_id: int
    title: str
    detail: str
    status: str
    priority: str
    created_at: datetime
