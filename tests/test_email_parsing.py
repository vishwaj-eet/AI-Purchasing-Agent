from app.tools.communication_tools import record_inbound_email
from app.agents.email_agent import parse_and_process_email
from app.models.email_message import EmailMessage

def test_email_parsing_order_confirmation(db):
    email = record_inbound_email(
        db=db,
        sender="sales@apexelectronics.com",
        subject="Order Confirmation PO-1048",
        body="Dear Team, We acknowledge and accept PO-1048. All 500 units of SKU-ELEC-001 will ship tomorrow."
    )

    parsed = parse_and_process_email(db, email.id, trace_id="test-trace-1")
    assert parsed["intent"] == "ORDER_CONFIRMATION"
    assert parsed["po_reference"] == "PO-1048"
    assert parsed["sentiment"] == "POSITIVE"

def test_email_parsing_shipment_delay(db):
    email = record_inbound_email(
        db=db,
        sender="orders@novapackaging.com",
        subject="Production delay on PO-1049",
        body="Attention: Due to mill maintenance, PO-1049 for packaging is delayed by 10 days."
    )

    parsed = parse_and_process_email(db, email.id, trace_id="test-trace-2")
    assert parsed["intent"] == "SHIPMENT_DELAY"
    assert parsed["po_reference"] == "PO-1049"
    assert parsed["sentiment"] == "CRITICAL"
