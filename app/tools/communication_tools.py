import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.email_message import EmailMessage
from app.models.purchase_order import PurchaseOrder

logger = logging.getLogger(__name__)

def record_outbound_email(
    db: Session,
    recipient: str,
    subject: str,
    body: str,
    thread_id: Optional[str] = None,
    po_reference_id: Optional[int] = None
) -> EmailMessage:
    """Dispatches and logs an outbound communication to a supplier or stakeholder."""
    msg_id = f"out-{uuid.uuid4().hex[:10]}"
    email = EmailMessage(
        message_id=msg_id,
        thread_id=thread_id or f"th-{msg_id}",
        sender="procurement@enterprise.internal",
        recipient=recipient,
        subject=subject,
        body=body,
        direction="OUTBOUND",
        status="SENT",
        po_reference_id=po_reference_id,
        created_at=datetime.utcnow()
    )
    db.add(email)
    db.commit()
    logger.info(f"Outbound email dispatched to {recipient}: '{subject}'")
    return email

def record_inbound_email(
    db: Session,
    sender: str,
    subject: str,
    body: str,
    thread_id: Optional[str] = None
) -> EmailMessage:
    """Registers an incoming supplier message in the enterprise inbox."""
    msg_id = f"in-{uuid.uuid4().hex[:10]}"
    email = EmailMessage(
        message_id=msg_id,
        thread_id=thread_id or f"th-{msg_id}",
        sender=sender,
        recipient="procurement@enterprise.internal",
        subject=subject,
        body=body,
        direction="INBOUND",
        status="RECEIVED",
        created_at=datetime.utcnow()
    )
    db.add(email)
    db.commit()
    return email
