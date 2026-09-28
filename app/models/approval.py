from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    status = Column(String(30), default="PENDING")  # PENDING, APPROVED, REJECTED, MODIFIED
    required_role = Column(String(50), default="BUYER")  # BUYER, MANAGER, VP
    trigger_reason = Column(String(255), nullable=False)  # e.g. "Amount exceeds $5,000 auto-limit ($7,450.00)"
    risk_level = Column(String(20), default="MEDIUM")     # LOW, MEDIUM, HIGH, CRITICAL

    requested_amount = Column(Float, nullable=False)
    agent_reasoning = Column(Text, nullable=False)
    policy_citations = Column(Text, nullable=True)  # JSON or text citation from RAG SOPs

    # Human reviewer feedback
    reviewer_user = Column(String(100), nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    modification_details = Column(Text, nullable=True)  # if modified before approval
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    purchase_order = relationship("PurchaseOrder", back_populates="approval_requests")
