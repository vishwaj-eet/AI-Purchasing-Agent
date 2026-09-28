from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate
from app.tools.inventory_tools import update_inventory_stock

router = APIRouter(prefix="/api/inventory", tags=["Inventory & Demand"])

@router.get("", response_model=List[ProductResponse])
def get_all_inventory(category: Optional[str] = None, below_reorder_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(Product).filter(Product.is_active == True)
    if category:
        query = query.filter(Product.category == category)
    products = query.all()

    if below_reorder_only:
        products = [p for p in products if p.is_below_reorder_point]

    return products

@router.get("/{sku}", response_model=ProductResponse)
def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter_by(sku=sku).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with SKU '{sku}' not found")
    return product

@router.post("", response_model=ProductResponse, status_code=201)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    if db.query(Product).filter_by(sku=product_in.sku).first():
        raise HTTPException(status_code=400, detail=f"Product SKU '{product_in.sku}' already exists")
    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.put("/{sku}/adjust")
def adjust_product_stock(sku: str, quantity_delta: int, db: Session = Depends(get_db)):
    success = update_inventory_stock(db, sku, quantity_delta)
    if not success:
        raise HTTPException(status_code=404, detail=f"Product with SKU '{sku}' not found")
    product = db.query(Product).filter_by(sku=sku).first()
    return {
        "message": f"Stock adjusted by {quantity_delta}",
        "sku": product.sku,
        "current_stock": product.current_stock,
        "is_below_reorder_point": product.is_below_reorder_point
    }
