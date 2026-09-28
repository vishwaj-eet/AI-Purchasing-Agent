from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/api/audit", tags=["Audit & Tracing"])

@router.get("/logs")
def get_audit_logs(
    trace_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Fetches chronological audit logs and execution traces for all agent actions."""
    query = db.query(AuditLog)
    if trace_id:
        query = query.filter(AuditLog.trace_id == trace_id)
    if agent_name:
        query = query.filter(AuditLog.agent_name == agent_name)
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": l.id,
            "trace_id": l.trace_id,
            "agent_name": l.agent_name,
            "step_name": l.step_name,
            "event_type": l.event_type,
            "input_payload": l.input_payload,
            "output_payload": l.output_payload,
            "status": l.status,
            "timestamp": l.timestamp.isoformat()
        }
        for l in logs
    ]

@router.get("/traces")
def get_recent_traces(db: Session = Depends(get_db)):
    """Groups recent audit events by trace_id to display end-to-end execution histories."""
    distinct_traces = (
        db.query(AuditLog.trace_id)
        .distinct()
        .order_by(AuditLog.timestamp.desc())
        .limit(20)
        .all()
    )

    traces_summary = []
    for (t_id,) in distinct_traces:
        events = db.query(AuditLog).filter_by(trace_id=t_id).order_by(AuditLog.timestamp.asc()).all()
        if events:
            traces_summary.append({
                "trace_id": t_id,
                "start_time": events[0].timestamp.isoformat(),
                "steps_count": len(events),
                "agents_involved": list(set(e.agent_name for e in events)),
                "has_escalation": any(e.event_type == "HITL_ESCALATION" for e in events)
            })

    return traces_summary
