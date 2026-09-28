from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.approval import ApprovalRequest
from app.schemas.workflow import ApprovalResponse, ApprovalDecisionRequest
from app.tools.procurement_tools import resolve_human_approval

router = APIRouter(prefix="/api/approvals", tags=["Human-in-the-Loop Approvals"])

@router.get("", response_model=List[ApprovalResponse])
def get_approvals(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ApprovalRequest)
    if status:
        query = query.filter(ApprovalRequest.status == status.upper())
    return query.order_by(ApprovalRequest.created_at.desc()).all()

@router.get("/{approval_id}", response_model=ApprovalResponse)
def get_approval(approval_id: int, db: Session = Depends(get_db)):
    approval = db.query(ApprovalRequest).filter_by(id=approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return approval

@router.post("/{approval_id}/decide")
def submit_approval_decision(
    approval_id: int,
    decision_in: ApprovalDecisionRequest,
    db: Session = Depends(get_db)
):
    """
    Submits a buyer decision for an escalated action:
    - APPROVE: Authorizes the agent to transmit the PO.
    - REJECT: Cancels the purchase order.
    - MODIFY: Updates quantities or prices, then transmits the revised PO.
    """
    try:
        result = resolve_human_approval(
            db=db,
            approval_id=approval_id,
            decision=decision_in.decision,
            reviewer_user=decision_in.reviewer_user,
            reviewer_notes=decision_in.reviewer_notes,
            modified_qty=decision_in.modified_quantity,
            modified_price=decision_in.modified_price
        )
        return {
            "status": "SUCCESS",
            "message": f"Approval request {approval_id} resolved with decision '{decision_in.decision}'.",
            "result": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
