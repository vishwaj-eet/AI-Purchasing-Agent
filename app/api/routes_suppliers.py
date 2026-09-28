from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.supplier import Supplier, SupplierCatalog
from app.schemas.supplier import SupplierResponse, SupplierCreate, SupplierCatalogBase, SupplierCatalogResponse

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers & Vendors"])

@router.get("", response_model=List[SupplierResponse])
def get_all_suppliers(approved_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(Supplier)
    if approved_only:
        query = query.filter(Supplier.is_approved == True)
    return query.all()

@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter_by(id=supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.post("", response_model=SupplierResponse, status_code=201)
def create_supplier(supplier_in: SupplierCreate, db: Session = Depends(get_db)):
    if db.query(Supplier).filter_by(code=supplier_in.code).first():
        raise HTTPException(status_code=400, detail=f"Supplier code '{supplier_in.code}' already exists")
    supplier = Supplier(**supplier_in.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier

@router.post("/{supplier_id}/catalog", response_model=SupplierCatalogResponse, status_code=201)
def add_catalog_item(supplier_id: int, item_in: SupplierCatalogBase, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter_by(id=supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    cat_item = SupplierCatalog(supplier_id=supplier_id, **item_in.model_dump())
    db.add(cat_item)
    db.commit()
    db.refresh(cat_item)
    return cat_item
