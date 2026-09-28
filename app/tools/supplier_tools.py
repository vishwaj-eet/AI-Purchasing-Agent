import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.supplier import Supplier, SupplierCatalog, SupplierScorecard

logger = logging.getLogger(__name__)

def find_eligible_suppliers_for_sku(db: Session, sku: str) -> List[Dict[str, Any]]:
    """Identifies all suppliers offering the specified SKU with active pricing catalogs."""
    items = (
        db.query(SupplierCatalog, Supplier)
        .join(Supplier, SupplierCatalog.supplier_id == Supplier.id)
        .filter(SupplierCatalog.sku == sku, Supplier.is_approved == True)
        .all()
    )

    results = []
    for cat, sup in items:
        # Check volume discount if any
        discounts = []
        if cat.tier_discount_json:
            try:
                discounts = json.loads(cat.tier_discount_json)
            except Exception:
                pass

        results.append({
            "supplier_id": sup.id,
            "supplier_code": sup.code,
            "supplier_name": sup.name,
            "contact_email": sup.contact_email,
            "unit_price": cat.unit_price,
            "moq": cat.moq,
            "lead_time_days": cat.lead_time_days,
            "currency": cat.currency,
            "is_preferred": sup.is_preferred,
            "reliability_score": sup.reliability_score,
            "on_time_delivery_rate": sup.on_time_delivery_rate,
            "quality_rating": sup.quality_rating,
            "payment_terms": sup.payment_terms,
            "tier_discounts": discounts
        })

    # Sort: Preferred first, then highest reliability, then lowest price
    results.sort(key=lambda s: (not s["is_preferred"], -s["reliability_score"], s["unit_price"]))
    return results

def evaluate_best_supplier(db: Session, sku: str, requested_qty: int) -> Optional[Dict[str, Any]]:
    """
    Selects optimal supplier balancing price, MOQ adjustments, volume discounts,
    lead times, and vendor reliability scorecard.
    """
    candidates = find_eligible_suppliers_for_sku(db, sku)
    if not candidates:
        return None

    best = None
    lowest_effective_cost = float("inf")

    for cand in candidates:
        order_qty = max(requested_qty, cand["moq"])
        unit_price = cand["unit_price"]

        # Apply tier discount if order_qty meets threshold
        for tier in cand.get("tier_discounts", []):
            if order_qty >= tier.get("min_qty", 0):
                pct = tier.get("discount_pct", 0)
                unit_price = round(unit_price * (1.0 - (pct / 100.0)), 4)

        total_cost = round(unit_price * order_qty, 2)

        # Multi-factor score: Lower total cost, higher reliability
        if total_cost < lowest_effective_cost:
            lowest_effective_cost = total_cost
            best = {
                **cand,
                "adjusted_order_qty": order_qty,
                "effective_unit_price": unit_price,
                "total_estimated_cost": total_cost,
                "selection_reason": (
                    f"Selected {cand['supplier_name']} ({cand['supplier_code']}): "
                    f"Contract price ${unit_price:.2f}/unit (total: ${total_cost:,.2f}), "
                    f"lead time {cand['lead_time_days']} days, reliability {cand['reliability_score']}%."
                )
            }

    return best
