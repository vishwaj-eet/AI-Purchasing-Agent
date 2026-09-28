from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class EmailMessage(Base):
    __tablename__ = "email_messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(100), unique=True, index=True, nullable=False)
    thread_id = Column(String(100), index=True, nullable=True)
    sender = Column(String(150), nullable=False, index=True)
    recipient = Column(String(150), nullable=False)
    subject = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    direction = Column(String(20), default="INBOUND")  # INBOUND or OUTBOUND

    # AI Parsing Results
    parsed_intent = Column(String(50), nullable=True)  # ORDER_CONFIRMATION, SHIPMENT_DELAY, PRICE_INCREASE, QUOTE, INVOICE, GENERAL_INQUIRY
    parsed_entities_json = Column(Text, nullable=True) # JSON e.g. {"po_number": "PO-1049", "delivery_date": "2026-10-15", "delay_days": 10}
    sentiment = Column(String(20), nullable=True)      # POSITIVE, NEUTRAL, CRITICAL
    confidence_score = Column(Integer, default=95)

    po_reference_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)
    status = Column(String(30), default="PROCESSED")   # RECEIVED, PROCESSING, PROCESSED, ESCALATED
    created_at = Column(DateTime, default=datetime.utcnow)
