from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: str
    unit_of_measure: str = "PCS"
    unit_cost: float
    current_stock: int
    safety_stock: int
    reorder_point: int
    target_stock: int
    daily_demand_rate: float
    lead_time_days: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    current_stock: Optional[int] = None
    safety_stock: Optional[int] = None
    reorder_point: Optional[int] = None
    target_stock: Optional[int] = None
    daily_demand_rate: Optional[float] = None
    unit_cost: Optional[float] = None

class ProductResponse(ProductBase):
    id: int
    days_of_supply: float
    is_below_reorder_point: bool
    is_critical_stockout_risk: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

