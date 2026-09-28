import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.models.supplier import Supplier, SupplierScorecard

logger = logging.getLogger(__name__)

class AgentMemoryStore:
    """
    State and memory management across multi-step procurement workflows.
    Maintains workflow checkpoints, audit traces, and historical supplier interactions.
    """

    def __init__(self):
        # In-memory execution state checkpoints for active workflows
        self._active_checkpoints: Dict[str, Dict[str, Any]] = {}

    def save_checkpoint(self, trace_id: str, state_data: Dict[str, Any]):
        """Persists workflow state so it can be resumed after Human-in-the-loop review."""
        self._active_checkpoints[trace_id] = {
            "state": state_data,
            "saved_at": datetime.utcnow().isoformat()
        }

    def get_checkpoint(self, trace_id: str) -> Optional[Dict[str, Any]]:
        entry = self._active_checkpoints.get(trace_id)
        return entry["state"] if entry else None

    def log_trace(
        self,
        db: Session,
        trace_id: str,
        agent_name: str,
        step_name: str,
        event_type: str,
        input_payload: Any = None,
        output_payload: Any = None,
        status: str = "SUCCESS"
    ):
        """Records an immutable audit trace step to the database."""
        in_str = json.dumps(input_payload) if input_payload is not None and not isinstance(input_payload, str) else str(input_payload or "")
        out_str = json.dumps(output_payload) if output_payload is not None and not isinstance(output_payload, str) else str(output_payload or "")

        audit_entry = AuditLog(
            trace_id=trace_id,
            agent_name=agent_name,
            step_name=step_name,
            event_type=event_type,
            input_payload=in_str,
            output_payload=out_str,
            status=status,
            timestamp=datetime.utcnow()
        )
        db.add(audit_entry)
        db.commit()

    def update_supplier_behavior_memory(
        self,
        db: Session,
        supplier_id: int,
        is_on_time: bool,
        delay_days: float = 0.0,
        defect: bool = False,
        notes: str = ""
    ):
        """Updates long-term supplier scorecard and reliability metrics based on delivery outcomes."""
        scorecard = db.query(SupplierScorecard).filter_by(supplier_id=supplier_id).first()
        supplier = db.query(Supplier).filter_by(id=supplier_id).first()

        if not scorecard:
            scorecard = SupplierScorecard(supplier_id=supplier_id)
            db.add(scorecard)

        scorecard.total_orders += 1
        if is_on_time:
            scorecard.on_time_orders += 1
        else:
            scorecard.late_orders += 1
            scorecard.last_sla_breach = datetime.utcnow()
            scorecard.avg_delay_days = round((scorecard.avg_delay_days * (scorecard.late_orders - 1) + delay_days) / scorecard.late_orders, 1)

        if defect:
            scorecard.quality_defects += 1

        # Re-calculate supplier reliability rate
        if scorecard.total_orders > 0:
            delivery_rate = round((scorecard.on_time_orders / scorecard.total_orders) * 100.0, 1)
            scorecard.evaluated_at = datetime.utcnow()

            if supplier:
                supplier.on_time_delivery_rate = delivery_rate
                # Adjust composite reliability score
                defect_penalty = scorecard.quality_defects * 3.0
                delay_penalty = scorecard.avg_delay_days * 1.5
                supplier.reliability_score = max(50.0, min(100.0, round(delivery_rate - defect_penalty - delay_penalty, 1)))

        db.commit()

agent_memory = AgentMemoryStore()
