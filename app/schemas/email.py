from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class EmailIngestSchema(BaseModel):
    sender: str
    recipient: str = "procurement@enterprise.internal"
    subject: str
    body: str
    thread_id: Optional[str] = None

class EmailParseResult(BaseModel):
    intent: str
    confidence: int
    sentiment: str
    po_reference: Optional[str] = None
    sku_references: list[str] = []
    revised_delivery_date: Optional[str] = None
    delay_days: Optional[int] = None
    price_change_detected: bool = False
    action_required: str
    summary: str

class EmailResponse(BaseModel):
    id: int
    message_id: str
    thread_id: Optional[str] = None
    sender: str
    recipient: str
    subject: str
    body: str
    direction: str
    parsed_intent: Optional[str] = None
    parsed_entities_json: Optional[str] = None
    sentiment: Optional[str] = None
    confidence_score: Optional[int] = None
    po_reference_id: Optional[int] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

