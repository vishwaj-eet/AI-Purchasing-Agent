import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product

logger = logging.getLogger(__name__)

def check_inventory_levels(db: Session, sku: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches inventory positions, days of supply, and replenishment urgency flags."""
    query = db.query(Product).filter(Product.is_active == True)
    if sku:
        query = query.filter(Product.sku == sku)

    products = query.all()
    results = []
    for p in products:
        results.append({
            "sku": p.sku,
            "name": p.name,
            "category": p.category,
            "current_stock": p.current_stock,
            "safety_stock": p.safety_stock,
            "reorder_point": p.reorder_point,
            "target_stock": p.target_stock,
            "daily_demand_rate": p.daily_demand_rate,
            "days_of_supply": p.days_of_supply,
            "is_below_reorder_point": p.is_below_reorder_point,
            "is_critical_stockout_risk": p.is_critical_stockout_risk,
            "unit_cost": p.unit_cost
        })
    return results

def calculate_reorder_requirements(db: Session, sku: str) -> Optional[Dict[str, Any]]:
    """
    Computes required replenishment quantity based on target stock, current stock,
    safety stock buffer, and daily consumption velocity.
    """
    product = db.query(Product).filter_by(sku=sku).first()
    if not product:
        return None

    shortage = max(0, product.reorder_point - product.current_stock)
    recommended_order_qty = max(0, product.target_stock - product.current_stock)

    urgency = "NORMAL"
    if product.is_critical_stockout_risk:
        urgency = "CRITICAL_STOCKOUT_RISK"
    elif product.is_below_reorder_point:
        urgency = "REORDER_TRIGGERED"

    return {
        "sku": product.sku,
        "name": product.name,
        "category": product.category,
        "current_stock": product.current_stock,
        "reorder_point": product.reorder_point,
        "target_stock": product.target_stock,
        "recommended_quantity": recommended_order_qty,
        "days_of_supply_remaining": product.days_of_supply,
        "urgency": urgency,
        "lead_time_days": product.lead_time_days
    }

def update_inventory_stock(db: Session, sku: str, quantity_delta: int) -> bool:
    """Adjusts on-hand inventory (e.g. upon goods receipt or stock allocation)."""
    product = db.query(Product).filter_by(sku=sku).first()
    if not product:
        return False
    product.current_stock = max(0, product.current_stock + quantity_delta)
    db.commit()
    return True
