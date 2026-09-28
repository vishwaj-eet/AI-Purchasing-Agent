from typing import TypedDict, List, Dict, Any, Optional

class ProcurementWorkflowState(TypedDict, total=False):
    trace_id: str
    trigger_type: str  # "SCHEDULED_REPLENISHMENT", "INBOUND_EMAIL", "MANUAL_SKU"
    target_sku: Optional[str]
    email_id: Optional[int]

    # Email Agent outputs
    inbound_email: Optional[Dict[str, Any]]
    parsed_email: Optional[Dict[str, Any]]

    # Inventory Agent outputs
    inventory_items: List[Dict[str, Any]]
    reorder_candidates: List[Dict[str, Any]]

    # Sourcing Agent outputs
    sourcing_recommendations: List[Dict[str, Any]]

    # RAG knowledge context
    rag_retrievals: List[Dict[str, Any]]

    # Guardrails outputs
    guardrail_results: List[Dict[str, Any]]

    # Final execution outputs
    generated_pos: List[Dict[str, Any]]
    escalations: List[Dict[str, Any]]
    outbound_emails: List[Dict[str, Any]]
    audit_trace: List[Dict[str, Any]]

    # Workflow lifecycle
    status: str  # "IN_PROGRESS", "COMPLETED", "ESCALATED_TO_HUMAN", "REJECTED_BY_GUARDRAIL", "FAILED"
    error: Optional[str]
