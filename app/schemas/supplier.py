from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

class SupplierCatalogBase(BaseModel):
    sku: str
    supplier_part_number: Optional[str] = None
    unit_price: float
    moq: int = 1
    lead_time_days: int = 7
    currency: str = "USD"
    tier_discount_json: Optional[str] = None

class SupplierCatalogResponse(SupplierCatalogBase):
    id: int
    supplier_id: int
    effective_date: datetime

    model_config = ConfigDict(from_attributes=True)

class SupplierScorecardResponse(BaseModel):
    id: int
    supplier_id: int
    total_orders: int
    on_time_orders: int
    late_orders: int
    quality_defects: int
    avg_delay_days: float
    last_sla_breach: Optional[datetime] = None
    notes: Optional[str] = None
    evaluated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SupplierBase(BaseModel):
    code: str
    name: str
    contact_name: Optional[str] = None
    contact_email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: str = "Net 30"
    currency: str = "USD"
    is_preferred: bool = False
    is_approved: bool = True
    notes: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: int
    reliability_score: float
    on_time_delivery_rate: float
    quality_rating: float
    price_competitiveness_score: float
    created_at: datetime
    updated_at: datetime
    catalog_items: List[SupplierCatalogResponse] = []
    scorecards: List[SupplierScorecardResponse] = []

    model_config = ConfigDict(from_attributes=True)

