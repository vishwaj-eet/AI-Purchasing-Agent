from app.tools.procurement_tools import (
    create_purchase_order_record,
    create_human_escalation_request,
    resolve_human_approval
)
from app.models.purchase_order import POStatus, PurchaseOrder
from app.models.approval import ApprovalRequest

def test_hitl_escalation_and_approval(db):
    # 1. Create a PO
    items = [{"sku": "SKU-ELEC-001", "description": "STM32F4", "quantity": 1000, "unit_price": 8.45}]
    po = create_purchase_order_record(
        db=db,
        supplier_id=1,
        items=items,
        status=POStatus.DRAFT.value
    )

    # 2. Escalate to HITL
    approval_req = create_human_escalation_request(
        db=db,
        po_id=po.id,
        trigger_reason="Order amount ($8,450.00) exceeds $5,000 threshold",
        risk_level="MEDIUM",
        required_role="BUYER",
        agent_reasoning="Volume order for production schedule.",
        policy_citations="SOP-PROC-001"
    )

    assert approval_req.status == "PENDING"
    assert po.status == POStatus.PENDING_APPROVAL.value

    # 3. Resolve approval (APPROVE)
    res = resolve_human_approval(
        db=db,
        approval_id=approval_req.id,
        decision="APPROVE",
        reviewer_user="senior_buyer@enterprise.internal",
        reviewer_notes="Approved for Q3 manufacturing build."
    )

    assert res["decision"] == "APPROVE"
    assert res["po_status"] == POStatus.TRANSMITTED.value

def test_hitl_modification_and_approval(db):
    items = [{"sku": "SKU-PACK-001", "description": "Boxes", "quantity": 1000, "unit_price": 2.30}]
    po = create_purchase_order_record(db=db, supplier_id=2, items=items, status=POStatus.DRAFT.value)

    approval_req = create_human_escalation_request(
        db=db,
        po_id=po.id,
        trigger_reason="Requires buyer signoff",
        risk_level="LOW",
        required_role="BUYER",
        agent_reasoning="Packaging bulk replenishment"
    )

    # Modify quantity down to 500
    res = resolve_human_approval(
        db=db,
        approval_id=approval_req.id,
        decision="MODIFY",
        reviewer_user="lead_buyer@enterprise.internal",
        modified_qty=500
    )

    assert res["decision"] == "APPROVED_WITH_MODIFICATION"
    updated_po = db.query(PurchaseOrder).filter_by(id=po.id).first()
    assert updated_po.line_items[0].quantity == 500
    assert updated_po.total_amount == 1150.00
