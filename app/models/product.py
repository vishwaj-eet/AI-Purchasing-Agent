from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(100), nullable=False)  # Electronics, Packaging, Fasteners, Raw Materials
    unit_of_measure = Column(String(20), default="PCS")
    unit_cost = Column(Float, nullable=False, default=0.0)

    # Inventory Metrics
    current_stock = Column(Integer, default=0)
    safety_stock = Column(Integer, default=50)
    reorder_point = Column(Integer, default=100)
    target_stock = Column(Integer, default=300)
    daily_demand_rate = Column(Float, default=5.0)  # average units consumed/day
    lead_time_days = Column(Integer, default=7)    # standard supplier lead time

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def days_of_supply(self) -> float:
        if self.daily_demand_rate and self.daily_demand_rate > 0:
            return round(self.current_stock / self.daily_demand_rate, 1)
        return 999.0

    @property
    def is_below_reorder_point(self) -> bool:
        return self.current_stock <= self.reorder_point

    @property
    def is_critical_stockout_risk(self) -> bool:
        return self.current_stock <= self.safety_stock
