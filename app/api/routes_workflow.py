from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.schemas.workflow import WorkflowRunRequest, WorkflowRunResponse
from app.agents.orchestrator import orchestrator
from app.memory.agent_memory import agent_memory

router = APIRouter(prefix="/api/workflow", tags=["Agent Workflow Orchestration"])

@router.post("/run", response_model=WorkflowRunResponse)
def execute_procurement_workflow(req: WorkflowRunRequest):
    """
    Triggers end-to-end multi-agent supply chain replenishment run:
    - Analyzes inventory positions and consumption velocity
    - Sourcing selection and pricing optimization
    - RAG contract retrieval
    - Strict financial and policy guardrail verification
    - Autonomous PO transmission or HITL escalation.
    """
    result = orchestrator.run_workflow(
        trigger_type=req.trigger_type,
        target_sku=req.target_sku,
        email_id=req.email_id
    )
    return result

@router.get("/checkpoint/{trace_id}")
def get_workflow_checkpoint(trace_id: str):
    """Fetches saved workflow state checkpoint from agent memory."""
    state = agent_memory.get_checkpoint(trace_id)
    if not state:
        raise HTTPException(status_code=404, detail="Checkpoint not found for trace_id")
    return {"trace_id": trace_id, "state": state}
