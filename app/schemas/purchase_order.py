from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class LineItemSchema(BaseModel):
    sku: str
    description: Optional[str] = None
    quantity: int
    unit_price: float
    subtotal: float

class LineItemResponse(LineItemSchema):
    id: int
    po_id: int

    model_config = ConfigDict(from_attributes=True)

class POCreate(BaseModel):
    supplier_id: int
    items: List[LineItemSchema]
    notes: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None

class POUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None
    vendor_confirmation_ref: Optional[str] = None

class POResponse(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    status: str
    total_amount: float
    currency: str
    approval_tier: str
    risk_score: float
    risk_reasons: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    vendor_confirmation_ref: Optional[str] = None
    notes: Optional[str] = None
    agent_generated: int
    created_at: datetime
    updated_at: datetime
    line_items: List[LineItemResponse] = []

    model_config = ConfigDict(from_attributes=True)

