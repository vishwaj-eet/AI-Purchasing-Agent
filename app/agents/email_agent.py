import json
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.email_message import EmailMessage
from app.models.purchase_order import PurchaseOrder, POStatus
from app.core.llm_provider import llm_provider
from app.memory.agent_memory import agent_memory

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert Autonomous Supply Chain Email Triage Agent.
Your duty is to parse incoming communications from vendors, extract procurement entities,
classify the message intent, detect delays, price changes, or confirmations, and determine
immediate operational responses. Output strictly valid JSON matching this schema:
{
  "intent": "ORDER_CONFIRMATION | SHIPMENT_DELAY | PRICE_INCREASE | QUOTE | INVOICE | GENERAL_INQUIRY",
  "confidence": 95,
  "sentiment": "POSITIVE | NEUTRAL | CRITICAL",
  "po_reference": "PO-XXXX" or null,
  "sku_references": ["SKU-XXX"],
  "revised_delivery_date": "YYYY-MM-DD" or null,
  "delay_days": integer or null,
  "price_change_detected": boolean,
  "action_required": "string describing next operational action",
  "summary": "1-2 sentence executive summary"
}
"""

def parse_and_process_email(db: Session, email_id: int, trace_id: str) -> Dict[str, Any]:
    """Processes an incoming supplier email and extracts procurement signals."""
    email = db.query(EmailMessage).filter_by(id=email_id).first()
    if not email:
        raise ValueError(f"Email ID {email_id} not found")

    user_prompt = (
        f"Incoming Email Metadata:\n"
        f"Sender: {email.sender}\n"
        f"Subject: {email.subject}\n"
        f"Body:\n{email.body}\n"
    )

    llm_output = llm_provider.generate_completion(SYSTEM_PROMPT, user_prompt, json_mode=True)
    try:
        parsed = json.loads(llm_output)
    except Exception as e:
        logger.error(f"Failed to decode LLM response: {e}. Output was: {llm_output}")
        parsed = {
            "intent": "GENERAL_INQUIRY",
            "confidence": 60,
            "sentiment": "NEUTRAL",
            "po_reference": None,
            "sku_references": [],
            "action_required": "MANUAL_REVIEW",
            "summary": "Parsing fallback triggered."
        }

    # Update email record
    email.parsed_intent = parsed.get("intent")
    email.parsed_entities_json = json.dumps(parsed)
    email.sentiment = parsed.get("sentiment")
    email.confidence_score = parsed.get("confidence", 90)
    email.status = "PROCESSED"

    # Match PO reference if present
    po_ref = parsed.get("po_reference")
    linked_po = None
    if po_ref:
        linked_po = db.query(PurchaseOrder).filter_by(po_number=po_ref).first()
        if linked_po:
            email.po_reference_id = linked_po.id
            if parsed.get("intent") == "ORDER_CONFIRMATION":
                linked_po.status = POStatus.ACKNOWLEDGED.value
                linked_po.vendor_confirmation_ref = email.message_id
            elif parsed.get("intent") == "SHIPMENT_DELAY":
                delay_days = parsed.get("delay_days") or 5
                linked_po.notes = f"{linked_po.notes or ''} [ALERT: Supplier reported {delay_days}d delay]"
                # Update supplier scorecard memory
                agent_memory.update_supplier_behavior_memory(
                    db=db,
                    supplier_id=linked_po.supplier_id,
                    is_on_time=False,
                    delay_days=float(delay_days),
                    notes=f"Shipment delay on {po_ref}: {email.subject}"
                )

    db.commit()

    agent_memory.log_trace(
        db=db,
        trace_id=trace_id,
        agent_name="EmailTriageAgent",
        step_name="parse_incoming_communication",
        event_type="EMAIL_PARSED",
        input_payload={"email_id": email_id, "subject": email.subject},
        output_payload=parsed,
        status="SUCCESS"
    )

    return parsed
