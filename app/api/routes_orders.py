from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.purchase_order import PurchaseOrder
from app.schemas.purchase_order import POResponse, POCreate, POUpdate
from app.tools.procurement_tools import create_purchase_order_record

router = APIRouter(prefix="/api/orders", tags=["Purchase Orders"])

@router.get("", response_model=List[POResponse])
def get_orders(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(PurchaseOrder)
    if status:
        query = query.filter(PurchaseOrder.status == status.upper())
    return query.order_by(PurchaseOrder.created_at.desc()).all()

@router.get("/{po_id}", response_model=POResponse)
def get_order(po_id: int, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter_by(id=po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po

@router.post("", response_model=POResponse, status_code=201)
def create_manual_order(order_in: POCreate, db: Session = Depends(get_db)):
    items_data = [item.model_dump() for item in order_in.items]
    po = create_purchase_order_record(
        db=db,
        supplier_id=order_in.supplier_id,
        items=items_data,
        status="DRAFT",
        expected_delivery_date=order_in.expected_delivery_date,
        notes=order_in.notes
    )
    po.agent_generated = 0
    db.commit()
    db.refresh(po)
    return po

@router.put("/{po_id}/status", response_model=POResponse)
def update_order_status(po_id: int, update_in: POUpdate, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter_by(id=po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    if update_in.status:
        po.status = update_in.status.upper()
    if update_in.notes:
        po.notes = update_in.notes
    if update_in.expected_delivery_date:
        po.expected_delivery_date = update_in.expected_delivery_date
    if update_in.vendor_confirmation_ref:
        po.vendor_confirmation_ref = update_in.vendor_confirmation_ref
    db.commit()
    db.refresh(po)
    return po
