from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class WorkflowRunRequest(BaseModel):
    trigger_type: str = "SCHEDULED_REPLENISHMENT"  # "SCHEDULED_REPLENISHMENT", "INBOUND_EMAIL", "MANUAL_SKU"
    target_sku: Optional[str] = None
    email_id: Optional[int] = None
    simulation_override: bool = False

class TraceStep(BaseModel):
    agent: str
    step: str
    action: str
    details: Dict[str, Any]
    status: str = "SUCCESS"
    timestamp: datetime = datetime.utcnow()

class WorkflowRunResponse(BaseModel):
    trace_id: str
    trigger_type: str
    status: str  # "COMPLETED", "ESCALATED_TO_HUMAN", "REJECTED_BY_GUARDRAIL", "FAILED"
    recommendations: List[Dict[str, Any]] = []
    generated_pos: List[Dict[str, Any]] = []
    escalations: List[Dict[str, Any]] = []
    audit_trace: List[TraceStep] = []
    summary_message: str

class ApprovalDecisionRequest(BaseModel):
    decision: str  # "APPROVE", "REJECT", "MODIFY"
    reviewer_user: str = "buyer@enterprise.internal"
    reviewer_notes: Optional[str] = None
    modified_quantity: Optional[int] = None
    modified_price: Optional[float] = None

class ApprovalResponse(BaseModel):
    id: int
    po_id: int
    status: str
    required_role: str
    trigger_reason: str
    risk_level: str
    requested_amount: float
    agent_reasoning: str
    policy_citations: Optional[str] = None
    reviewer_user: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

