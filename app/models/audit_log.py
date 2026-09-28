from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String(100), index=True, nullable=False)
    agent_name = Column(String(100), nullable=False)  # e.g. "InventoryAnalystAgent", "GuardrailOfficer"
    step_name = Column(String(100), nullable=False)
    event_type = Column(String(50), nullable=False)   # TOOL_CALL, REASONING, GUARDRAIL_CHECK, STATE_CHANGE, HITL_ESCALATION
    input_payload = Column(Text, nullable=True)
    output_payload = Column(Text, nullable=True)
    status = Column(String(30), default="SUCCESS")     # SUCCESS, WARNING, REJECTED, FAILED
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
