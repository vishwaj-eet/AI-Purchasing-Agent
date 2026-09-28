from app.tools.inventory_tools import check_inventory_levels, calculate_reorder_requirements, update_inventory_stock
from app.models.product import Product

def test_check_inventory_levels(db):
    items = check_inventory_levels(db)
    assert len(items) >= 7
    skus = [i["sku"] for i in items]
    assert "SKU-ELEC-001" in skus
    assert "SKU-ELEC-002" in skus

def test_calculate_reorder_requirements(db):
    # SKU-ELEC-002 has 42 units, safety stock is 80, reorder point is 160
    reorder = calculate_reorder_requirements(db, "SKU-ELEC-002")
    assert reorder is not None
    assert reorder["urgency"] == "CRITICAL_STOCKOUT_RISK"
    assert reorder["recommended_quantity"] > 0
    assert reorder["days_of_supply_remaining"] < 7.0

def test_update_inventory_stock(db):
    initial = db.query(Product).filter_by(sku="SKU-ELEC-003").first().current_stock
    success = update_inventory_stock(db, "SKU-ELEC-003", 50)
    assert success is True

    updated = db.query(Product).filter_by(sku="SKU-ELEC-003").first().current_stock
    assert updated == initial + 50
