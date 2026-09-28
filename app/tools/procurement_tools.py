import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.purchase_order import PurchaseOrder, POLineItem, POStatus, ApprovalTier
from app.models.approval import ApprovalRequest
from app.models.supplier import Supplier

logger = logging.getLogger(__name__)

def create_purchase_order_record(
    db: Session,
    supplier_id: int,
    items: List[Dict[str, Any]],
    status: str = POStatus.DRAFT.value,
    approval_tier: str = ApprovalTier.AUTO.value,
    risk_score: float = 0.0,
    risk_reasons: Optional[List[str]] = None,
    expected_delivery_date: Optional[datetime] = None,
    notes: Optional[str] = None
) -> PurchaseOrder:
    """Creates a new purchase order with line items and financial totals."""
    # Generate unique PO number e.g. PO-5821
    po_num = f"PO-{random.randint(1100, 9999)}"
    while db.query(PurchaseOrder).filter_by(po_number=po_num).first():
        po_num = f"PO-{random.randint(1100, 9999)}"

    total_amount = sum(item["quantity"] * item["unit_price"] for item in items)
    reasons_json = json.dumps(risk_reasons or [])

    po = PurchaseOrder(
        po_number=po_num,
        supplier_id=supplier_id,
        status=status,
        total_amount=round(total_amount, 2),
        approval_tier=approval_tier,
        risk_score=risk_score,
        risk_reasons=reasons_json,
        expected_delivery_date=expected_delivery_date or (datetime.utcnow() + timedelta(days=5)),
        agent_generated=1,
        notes=notes
    )
    db.add(po)
    db.commit()

    for item in items:
        subtotal = round(item["quantity"] * item["unit_price"], 2)
        li = POLineItem(
            po_id=po.id,
            sku=item["sku"],
            description=item.get("description", item["sku"]),
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            subtotal=subtotal
        )
        db.add(li)

    db.commit()
    return po

def create_human_escalation_request(
    db: Session,
    po_id: int,
    trigger_reason: str,
    risk_level: str,
    required_role: str,
    agent_reasoning: str,
    policy_citations: Optional[str] = None
) -> ApprovalRequest:
    """Escalates a high-risk, ambiguous, or threshold-exceeding PO to the buyer approval queue."""
    po = db.query(PurchaseOrder).filter_by(id=po_id).first()
    if not po:
        raise ValueError(f"PO {po_id} not found")

    po.status = POStatus.PENDING_APPROVAL.value
    db.commit()

    approval_req = ApprovalRequest(
        po_id=po_id,
        status="PENDING",
        required_role=required_role,
        trigger_reason=trigger_reason,
        risk_level=risk_level,
        requested_amount=po.total_amount,
        agent_reasoning=agent_reasoning,
        policy_citations=policy_citations
    )
    db.add(approval_req)
    db.commit()
    return approval_req

def resolve_human_approval(
    db: Session,
    approval_id: int,
    decision: str,
    reviewer_user: str,
    reviewer_notes: Optional[str] = None,
    modified_qty: Optional[int] = None,
    modified_price: Optional[float] = None
) -> Dict[str, Any]:
    """Applies human buyer review: APPROVE, REJECT, or MODIFY."""
    approval = db.query(ApprovalRequest).filter_by(id=approval_id).first()
    if not approval:
        raise ValueError(f"Approval request {approval_id} not found")

    po = db.query(PurchaseOrder).filter_by(id=approval.po_id).first()
    if not po:
        raise ValueError(f"PO {approval.po_id} not found")

    decision = decision.upper()
    approval.status = decision
    approval.reviewer_user = reviewer_user
    approval.reviewer_notes = reviewer_notes
    approval.reviewed_at = datetime.utcnow()

    if decision == "APPROVE":
        po.status = POStatus.TRANSMITTED.value
    elif decision == "REJECT":
        po.status = POStatus.REJECTED.value
    elif decision == "MODIFY":
        approval.status = "APPROVED_WITH_MODIFICATION"
        po.status = POStatus.TRANSMITTED.value
        # If line items were modified, adjust them
        if modified_qty or modified_price:
            for item in po.line_items:
                if modified_qty:
                    item.quantity = modified_qty
                if modified_price:
                    item.unit_price = modified_price
                item.subtotal = round(item.quantity * item.unit_price, 2)
            po.total_amount = sum(it.subtotal for it in po.line_items)

    db.commit()
    return {
        "approval_id": approval.id,
        "po_number": po.po_number,
        "decision": approval.status,
        "po_status": po.status,
        "total_amount": po.total_amount
    }
