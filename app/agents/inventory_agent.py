import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product
from app.tools.inventory_tools import calculate_reorder_requirements
from app.memory.agent_memory import agent_memory

logger = logging.getLogger(__name__)

def analyze_inventory_and_demand(
    db: Session,
    trace_id: str,
    target_sku: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Scans inventory positions, calculates demand velocity and replenishment urgency,
    and produces candidate recommendations for purchasing.
    """
    query = db.query(Product).filter(Product.is_active == True)
    if target_sku:
        query = query.filter(Product.sku == target_sku)

    products = query.all()
    candidates = []

    for prod in products:
        reorder_info = calculate_reorder_requirements(db, prod.sku)
        if not reorder_info:
            continue

        # Trigger condition: Below reorder point or critical stockout risk
        if prod.is_below_reorder_point or prod.is_critical_stockout_risk or target_sku:
            candidates.append({
                "sku": prod.sku,
                "name": prod.name,
                "category": prod.category,
                "current_stock": prod.current_stock,
                "reorder_point": prod.reorder_point,
                "safety_stock": prod.safety_stock,
                "target_stock": prod.target_stock,
                "recommended_quantity": max(reorder_info["recommended_quantity"], 50),
                "days_of_supply": prod.days_of_supply,
                "urgency": reorder_info["urgency"],
                "unit_cost": prod.unit_cost
            })

    agent_memory.log_trace(
        db=db,
        trace_id=trace_id,
        agent_name="InventoryDemandAgent",
        step_name="analyze_stock_and_consumption",
        event_type="INVENTORY_EVALUATED",
        input_payload={"target_sku": target_sku, "total_skus_scanned": len(products)},
        output_payload={"candidate_count": len(candidates), "candidates": candidates},
        status="SUCCESS"
    )

    return candidates
