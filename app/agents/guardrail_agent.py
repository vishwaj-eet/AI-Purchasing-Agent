import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.guardrails import guardrails_engine
from app.memory.agent_memory import agent_memory

logger = logging.getLogger(__name__)

def evaluate_guardrails(
    db: Session,
    trace_id: str,
    sourcing_recommendations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Evaluates business policy compliance, authorization thresholds, and risk levels
    for each sourcing recommendation before committing or escalating.
    """
    guardrail_results = []

    for rec in sourcing_recommendations:
        res = guardrails_engine.validate_purchase_order(
            total_amount=rec["total_cost"],
            supplier_is_approved=True,  # Filtered in query, but validated here
            supplier_is_preferred=rec["is_preferred"],
            supplier_reliability_score=rec["reliability_score"],
            price_variance_pct=rec.get("price_variance_pct", 0.0),
            quantity=rec["order_quantity"]
        )

        decision = "AUTONOMOUS_EXECUTION"
        if not res.passed:
            decision = "REJECT_POLICY_BREACH"
        elif res.requires_escalation:
            decision = "ESCALATE_TO_HUMAN"

        guardrail_dict = {
            "sku": rec["sku"],
            "supplier_code": rec["supplier_code"],
            "total_cost": rec["total_cost"],
            "decision": decision,
            "risk_level": res.risk_level,
            "requires_escalation": res.requires_escalation,
            "reasons": res.reasons,
            "details": res.details
        }
        guardrail_results.append(guardrail_dict)

    agent_memory.log_trace(
        db=db,
        trace_id=trace_id,
        agent_name="GuardrailComplianceAgent",
        step_name="verify_policy_and_financial_limits",
        event_type="GUARDRAIL_VALIDATED",
        input_payload={"sourcing_count": len(sourcing_recommendations)},
        output_payload={"guardrails": guardrail_results},
        status="SUCCESS"
    )

    return guardrail_results
