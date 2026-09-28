from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.email_message import EmailMessage
from app.schemas.email import EmailResponse, EmailIngestSchema
from app.tools.communication_tools import record_inbound_email
from app.agents.orchestrator import orchestrator

router = APIRouter(prefix="/api/emails", tags=["Supplier Email & Communications"])

@router.get("", response_model=List[EmailResponse])
def get_emails(direction: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(EmailMessage)
    if direction:
        query = query.filter(EmailMessage.direction == direction.upper())
    return query.order_by(EmailMessage.created_at.desc()).all()

@router.get("/{email_id}", response_model=EmailResponse)
def get_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(EmailMessage).filter_by(id=email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@router.post("/inbound", response_model=EmailResponse, status_code=201)
def simulate_inbound_email(
    email_in: EmailIngestSchema,
    auto_trigger_workflow: bool = True,
    db: Session = Depends(get_db)
):
    """
    Simulates receiving an email from a vendor and optionally triggers the
    LangGraph triage & replenishment workflow immediately.
    """
    msg = record_inbound_email(
        db=db,
        sender=email_in.sender,
        subject=email_in.subject,
        body=email_in.body,
        thread_id=email_in.thread_id
    )

    if auto_trigger_workflow:
        # Trigger orchestrator with this email
        orchestrator.run_workflow(
            trigger_type="INBOUND_EMAIL",
            email_id=msg.id
        )
        db.refresh(msg)

    return msg

@router.post("/{email_id}/triage")
def trigger_manual_triage(email_id: int, db: Session = Depends(get_db)):
    """Runs the LangGraph multi-agent triage on an existing email message."""
    email = db.query(EmailMessage).filter_by(id=email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    result = orchestrator.run_workflow(
        trigger_type="INBOUND_EMAIL",
        email_id=email.id
    )
    return result
