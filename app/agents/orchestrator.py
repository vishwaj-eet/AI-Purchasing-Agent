import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END

from app.database import SessionLocal
from app.agents.state import ProcurementWorkflowState
from app.agents.email_agent import parse_and_process_email
from app.agents.inventory_agent import analyze_inventory_and_demand
from app.agents.sourcing_agent import evaluate_sourcing_options
from app.agents.guardrail_agent import evaluate_guardrails
from app.tools.procurement_tools import create_purchase_order_record, create_human_escalation_request
from app.tools.communication_tools import record_outbound_email
from app.models.purchase_order import POStatus, ApprovalTier
from app.memory.agent_memory import agent_memory

logger = logging.getLogger(__name__)

class ProcurementWorkflowOrchestrator:
    """
    Production-grade multi-agent orchestrator using LangGraph StateGraph.
    Coordinates email triage, inventory analytics, sourcing, RAG policy retrieval,
    strict guardrails, and Human-In-The-Loop escalation.
    """

    def __init__(self):
        self.workflow_graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(ProcurementWorkflowState)

        # 1. Define Nodes
        graph.add_node("email_triage", self._node_email_triage)
        graph.add_node("inventory_analysis", self._node_inventory_analysis)
        graph.add_node("sourcing_selection", self._node_sourcing_selection)
        graph.add_node("guardrail_verification", self._node_guardrail_verification)
        graph.add_node("execution_and_escalation", self._node_execution_and_escalation)

        # 2. Define Entry Point & Routing
        graph.set_conditional_entry_point(
            self._route_entry,
            {
                "email_triage": "email_triage",
                "inventory_analysis": "inventory_analysis"
            }
        )

        # 3. Transitions
        graph.add_conditional_edges(
            "email_triage",
            self._route_after_email,
            {
                "inventory_analysis": "inventory_analysis",
                "end": END
            }
        )

        graph.add_conditional_edges(
            "inventory_analysis",
            self._route_after_inventory,
            {
                "sourcing_selection": "sourcing_selection",
                "end": END
            }
        )

        graph.add_edge("sourcing_selection", "guardrail_verification")
        graph.add_edge("guardrail_verification", "execution_and_escalation")
        graph.add_edge("execution_and_escalation", END)

        return graph.compile()

    # --- Router Functions ---
    def _route_entry(self, state: ProcurementWorkflowState) -> str:
        if state.get("trigger_type") == "INBOUND_EMAIL" and state.get("email_id"):
            return "email_triage"
        return "inventory_analysis"

    def _route_after_email(self, state: ProcurementWorkflowState) -> str:
        parsed = state.get("parsed_email") or {}
        # If shipment delay or price increase, analyze inventory impact
        if parsed.get("intent") in ["SHIPMENT_DELAY", "PRICE_INCREASE"]:
            return "inventory_analysis"
        # Pure confirmation or inquiry terminates here
        return "end"

    def _route_after_inventory(self, state: ProcurementWorkflowState) -> str:
        candidates = state.get("reorder_candidates", [])
        if candidates:
            return "sourcing_selection"
        return "end"

    # --- Node Executions ---
    def _node_email_triage(self, state: ProcurementWorkflowState) -> Dict[str, Any]:
        trace_id = state["trace_id"]
        email_id = state["email_id"]
        db = SessionLocal()
        try:
            parsed = parse_and_process_email(db, email_id, trace_id)
            # If SKU references were found in delay email, target that SKU
            target_sku = None
            if parsed.get("sku_references"):
                target_sku = parsed["sku_references"][0]

            return {
                "parsed_email": parsed,
                "target_sku": target_sku or state.get("target_sku"),
                "status": "EMAIL_TRIAGED"
            }
        finally:
            db.close()

    def _node_inventory_analysis(self, state: ProcurementWorkflowState) -> Dict[str, Any]:
        trace_id = state["trace_id"]
        target_sku = state.get("target_sku")
        db = SessionLocal()
        try:
            candidates = analyze_inventory_and_demand(db, trace_id, target_sku)
            return {
                "reorder_candidates": candidates,
                "status": "INVENTORY_ANALYZED"
            }
        finally:
            db.close()

    def _node_sourcing_selection(self, state: ProcurementWorkflowState) -> Dict[str, Any]:
        trace_id = state["trace_id"]
        candidates = state.get("reorder_candidates", [])
        db = SessionLocal()
        try:
            sourcing_recs, rag_snippets = evaluate_sourcing_options(db, trace_id, candidates)
            return {
                "sourcing_recommendations": sourcing_recs,
                "rag_retrievals": rag_snippets,
                "status": "SOURCING_EVALUATED"
            }
        finally:
            db.close()

    def _node_guardrail_verification(self, state: ProcurementWorkflowState) -> Dict[str, Any]:
        trace_id = state["trace_id"]
        sourcing_recs = state.get("sourcing_recommendations", [])
        db = SessionLocal()
        try:
            guardrails = evaluate_guardrails(db, trace_id, sourcing_recs)
            return {
                "guardrail_results": guardrails,
                "status": "GUARDRAILS_VERIFIED"
            }
        finally:
            db.close()

    def _node_execution_and_escalation(self, state: ProcurementWorkflowState) -> Dict[str, Any]:
        trace_id = state["trace_id"]
        sourcing_recs = state.get("sourcing_recommendations", [])
        guardrails = {g["sku"]: g for g in state.get("guardrail_results", [])}
        db = SessionLocal()

        generated_pos = []
        escalations = []
        outbound_emails = []

        try:
            for rec in sourcing_recs:
                sku = rec["sku"]
                guardrail = guardrails.get(sku, {})
                items = [{
                    "sku": sku,
                    "description": rec["product_name"],
                    "quantity": rec["order_quantity"],
                    "unit_price": rec["unit_price"]
                }]

                tier = ApprovalTier.AUTO.value
                if rec["total_cost"] > 100000:
                    tier = ApprovalTier.VP_OPERATIONS.value
                elif rec["total_cost"] > 25000:
                    tier = ApprovalTier.PROCUREMENT_MANAGER.value
                elif rec["total_cost"] > 5000:
                    tier = ApprovalTier.BUYER.value

                # Case A: Escalation Required (HITL)
                if guardrail.get("requires_escalation") or guardrail.get("decision") == "ESCALATE_TO_HUMAN":
                    po = create_purchase_order_record(
                        db=db,
                        supplier_id=rec["supplier_id"],
                        items=items,
                        status=POStatus.PENDING_APPROVAL.value,
                        approval_tier=tier,
                        risk_score=0.75 if guardrail.get("risk_level") == "HIGH" else 0.50,
                        risk_reasons=guardrail.get("reasons", []),
                        notes=f"Flagged by Guardrail Officer: {'; '.join(guardrail.get('reasons', []))}"
                    )

                    rag_context_str = json.dumps([c.get("title", "") for c in rec.get("rag_citations", [])])
                    approval_req = create_human_escalation_request(
                        db=db,
                        po_id=po.id,
                        trigger_reason="; ".join(guardrail.get("reasons", ["Approval threshold exceeded"])),
                        risk_level=guardrail.get("risk_level", "MEDIUM"),
                        required_role="BUYER" if tier in ["AUTO", "BUYER"] else "MANAGER",
                        agent_reasoning=rec["rationale"],
                        policy_citations=rag_context_str
                    )

                    escalations.append({
                        "approval_id": approval_req.id,
                        "po_number": po.po_number,
                        "po_id": po.id,
                        "total_amount": po.total_amount,
                        "reasons": guardrail.get("reasons", []),
                        "risk_level": approval_req.risk_level
                    })

                    agent_memory.log_trace(
                        db=db,
                        trace_id=trace_id,
                        agent_name="ProcurementWorkflowOrchestrator",
                        step_name="escalate_to_human_buyer",
                        event_type="HITL_ESCALATION",
                        input_payload={"po_id": po.id, "reasons": guardrail.get("reasons")},
                        output_payload={"approval_id": approval_req.id},
                        status="WARNING"
                    )

                # Case B: Autonomous PO Execution (Low risk, within policy)
                elif guardrail.get("decision") == "AUTONOMOUS_EXECUTION":
                    po = create_purchase_order_record(
                        db=db,
                        supplier_id=rec["supplier_id"],
                        items=items,
                        status=POStatus.TRANSMITTED.value,
                        approval_tier=ApprovalTier.AUTO.value,
                        risk_score=0.10,
                        risk_reasons=["Autonomous execution: within policy limits"],
                        notes="Autonomously executed by AI Procurement Agent."
                    )

                    # Dispatch Outbound PO Email to Supplier
                    email_body = (
                        f"Dear {rec['supplier_name']} Team,\n\n"
                        f"Please accept official Purchase Order {po.po_number}.\n\n"
                        f"Order Details:\n"
                        f"- SKU: {sku} ({rec['product_name']})\n"
                        f"- Quantity: {rec['order_quantity']}\n"
                        f"- Agreed Unit Price: ${rec['unit_price']:.2f}\n"
                        f"- Total Amount: ${po.total_amount:,.2f} USD\n"
                        f"- Delivery Terms: As per Master Agreement (Expected in {rec['lead_time_days']} business days)\n\n"
                        f"Kindly reply with order confirmation and shipment tracking details.\n\n"
                        f"Sincerely,\nAutonomous AI Procurement Agent\nProcurePulse Enterprise"
                    )
                    email_msg = record_outbound_email(
                        db=db,
                        recipient=rec["contact_email"],
                        subject=f"Purchase Order Issued: {po.po_number} - {sku}",
                        body=email_body,
                        thread_id=f"po-{po.po_number}",
                        po_reference_id=po.id
                    )

                    generated_pos.append({
                        "po_id": po.id,
                        "po_number": po.po_number,
                        "supplier_name": rec["supplier_name"],
                        "total_amount": po.total_amount,
                        "status": po.status,
                        "items_count": len(items)
                    })
                    outbound_emails.append({
                        "recipient": rec["contact_email"],
                        "subject": f"Purchase Order Issued: {po.po_number}"
                    })

                    agent_memory.log_trace(
                        db=db,
                        trace_id=trace_id,
                        agent_name="ProcurementWorkflowOrchestrator",
                        step_name="execute_purchase_order",
                        event_type="PO_TRANSMITTED",
                        input_payload={"po_number": po.po_number, "total_amount": po.total_amount},
                        output_payload={"email_id": email_msg.message_id},
                        status="SUCCESS"
                    )

            final_status = "COMPLETED"
            if escalations:
                final_status = "ESCALATED_TO_HUMAN"
            elif not generated_pos:
                final_status = "NO_REPLENISHMENT_NEEDED"

            return {
                "generated_pos": generated_pos,
                "escalations": escalations,
                "outbound_emails": outbound_emails,
                "status": final_status
            }
        finally:
            db.close()

    def run_workflow(
        self,
        trigger_type: str = "SCHEDULED_REPLENISHMENT",
        target_sku: Optional[str] = None,
        email_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Runs the complete multi-agent procurement workflow."""
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"

        initial_state: ProcurementWorkflowState = {
            "trace_id": trace_id,
            "trigger_type": trigger_type,
            "target_sku": target_sku,
            "email_id": email_id,
            "reorder_candidates": [],
            "sourcing_recommendations": [],
            "rag_retrievals": [],
            "guardrail_results": [],
            "generated_pos": [],
            "escalations": [],
            "outbound_emails": [],
            "status": "IN_PROGRESS"
        }

        # Execute LangGraph
        result_state = self.workflow_graph.invoke(initial_state)

        # Persist checkpoint in memory
        agent_memory.save_checkpoint(trace_id, result_state)

        summary_msg = f"Workflow finished with status '{result_state.get('status')}'. "
        if result_state.get("generated_pos"):
            summary_msg += f"Autonomously created & dispatched {len(result_state['generated_pos'])} PO(s). "
        if result_state.get("escalations"):
            summary_msg += f"Escalated {len(result_state['escalations'])} order(s) for Human-In-The-Loop buyer approval."

        return {
            "trace_id": trace_id,
            "trigger_type": trigger_type,
            "status": result_state.get("status", "COMPLETED"),
            "recommendations": result_state.get("sourcing_recommendations", []),
            "generated_pos": result_state.get("generated_pos", []),
            "escalations": result_state.get("escalations", []),
            "outbound_emails": result_state.get("outbound_emails", []),
            "summary_message": summary_msg
        }

orchestrator = ProcurementWorkflowOrchestrator()
