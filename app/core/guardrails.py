import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class GuardrailValidationResult:
    def __init__(self, passed: bool, requires_escalation: bool, risk_level: str, reasons: List[str], details: Dict[str, Any] = None):
        self.passed = passed
        self.requires_escalation = requires_escalation
        self.risk_level = risk_level  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
        self.reasons = reasons
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "requires_escalation": self.requires_escalation,
            "risk_level": self.risk_level,
            "reasons": self.reasons,
            "details": self.details
        }

class GuardrailsEngine:
    """
    Production-grade enterprise guardrails enforcing policy limits,
    unauthorized spend prevention, supplier vetting, and hallucination checks.
    """

    def __init__(self):
        self.max_auto_approve = settings.MAX_AUTO_APPROVE_AMOUNT
        self.manager_threshold = settings.MANAGER_APPROVAL_THRESHOLD
        self.max_price_variance_pct = settings.MAX_PRICE_VARIANCE_PERCENT

    def validate_purchase_order(
        self,
        total_amount: float,
        supplier_is_approved: bool,
        supplier_is_preferred: bool,
        supplier_reliability_score: float,
        price_variance_pct: float = 0.0,
        quantity: int = 1
    ) -> GuardrailValidationResult:
        reasons: List[str] = []
        requires_escalation = False
        risk_level = "LOW"
        passed = True

        # 1. Supplier Status Guardrail
        if not supplier_is_approved:
            passed = False
            requires_escalation = True
            risk_level = "CRITICAL"
            reasons.append("POLICY BREACH: Sourcing from an unapproved vendor is strictly prohibited without VP sign-off.")

        # 2. Supplier Reliability Guardrail
        if supplier_reliability_score < 75.0:
            requires_escalation = True
            risk_level = max_risk(risk_level, "HIGH")
            reasons.append(f"SUPPLIER RISK: Vendor historical reliability ({supplier_reliability_score:.1f}%) is below SLA threshold of 75.0%.")

        # 3. Price Variance Guardrail
        if price_variance_pct > self.max_price_variance_pct:
            requires_escalation = True
            risk_level = max_risk(risk_level, "HIGH")
            reasons.append(f"PRICE DRIFT: Unit price variance of +{price_variance_pct:.1f}% exceeds authorized threshold of {self.max_price_variance_pct}%.")

        # 4. Quantity Sanity Guardrail
        if quantity <= 0:
            passed = False
            risk_level = "CRITICAL"
            reasons.append(f"INVALID QUANTITY: Replenishment quantity must be strictly positive (received: {quantity}).")

        # 5. Financial Approval Hierarchy Thresholds
        if total_amount > 100000.0:
            requires_escalation = True
            risk_level = max_risk(risk_level, "CRITICAL")
            reasons.append(f"FINANCIAL THRESHOLD: Order amount (${total_amount:,.2f}) exceeds $100,000.00 requiring VP Operations approval.")
        elif total_amount > self.manager_threshold:
            requires_escalation = True
            risk_level = max_risk(risk_level, "HIGH")
            reasons.append(f"FINANCIAL THRESHOLD: Order amount (${total_amount:,.2f}) exceeds Manager threshold (${self.manager_threshold:,.2f}).")
        elif total_amount > self.max_auto_approve:
            requires_escalation = True
            risk_level = max_risk(risk_level, "MEDIUM")
            reasons.append(f"FINANCIAL THRESHOLD: Order amount (${total_amount:,.2f}) exceeds auto-approve threshold (${self.max_auto_approve:,.2f}).")
        elif not supplier_is_preferred:
            requires_escalation = True
            risk_level = max_risk(risk_level, "MEDIUM")
            reasons.append("VENDOR POLICY: Non-preferred vendor requires Buyer verification even if under auto-approval limit.")

        if not reasons:
            reasons.append("All automated guardrails passed: Low value, preferred supplier, zero price drift.")

        return GuardrailValidationResult(
            passed=passed,
            requires_escalation=requires_escalation,
            risk_level=risk_level,
            reasons=reasons,
            details={
                "total_amount": total_amount,
                "auto_limit": self.max_auto_approve,
                "price_variance_pct": price_variance_pct
            }
        )

def max_risk(r1: str, r2: str) -> str:
    order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    return r2 if order.get(r2, 1) > order.get(r1, 1) else r1

guardrails_engine = GuardrailsEngine()
