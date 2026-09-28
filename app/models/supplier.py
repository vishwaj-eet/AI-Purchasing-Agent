from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    contact_name = Column(String(100), nullable=True)
    contact_email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    address = Column(String(300), nullable=True)
    payment_terms = Column(String(50), default="Net 30")  # Net 30, Net 60, Advance
    currency = Column(String(10), default="USD")

    # Reliability & Performance Metrics
    reliability_score = Column(Float, default=95.0)  # 0 to 100
    on_time_delivery_rate = Column(Float, default=95.0)  # percentage
    quality_rating = Column(Float, default=4.8)  # 1.0 to 5.0
    price_competitiveness_score = Column(Float, default=90.0)

    is_preferred = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    catalog_items = relationship("SupplierCatalog", back_populates="supplier", cascade="all, delete-orphan")
    scorecards = relationship("SupplierScorecard", back_populates="supplier", cascade="all, delete-orphan")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

class SupplierCatalog(Base):
    __tablename__ = "supplier_catalogs"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    sku = Column(String(50), nullable=False, index=True)
    supplier_part_number = Column(String(100), nullable=True)
    unit_price = Column(Float, nullable=False)
    moq = Column(Integer, default=1)  # Minimum Order Quantity
    lead_time_days = Column(Integer, default=7)
    currency = Column(String(10), default="USD")
    tier_discount_json = Column(Text, nullable=True)  # JSON e.g. [{"min_qty": 500, "discount_pct": 5}]
    effective_date = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="catalog_items")

class SupplierScorecard(Base):
    __tablename__ = "supplier_scorecards"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    total_orders = Column(Integer, default=0)
    on_time_orders = Column(Integer, default=0)
    late_orders = Column(Integer, default=0)
    quality_defects = Column(Integer, default=0)
    avg_delay_days = Column(Float, default=0.0)
    last_sla_breach = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="scorecards")
