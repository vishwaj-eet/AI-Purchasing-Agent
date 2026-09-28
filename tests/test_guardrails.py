from app.core.guardrails import guardrails_engine

def test_guardrails_low_value_preferred_passes():
    # <= $5,000, preferred supplier, high reliability, zero price drift -> autonomous execution
    res = guardrails_engine.validate_purchase_order(
        total_amount=2500.00,
        supplier_is_approved=True,
        supplier_is_preferred=True,
        supplier_reliability_score=98.0,
        price_variance_pct=1.0,
        quantity=200
    )
    assert res.passed is True
    assert res.requires_escalation is False
    assert res.risk_level == "LOW"

def test_guardrails_high_value_requires_escalation():
    # $15,000 exceeds $5,000 auto limit -> must escalate to Buyer
    res = guardrails_engine.validate_purchase_order(
        total_amount=15000.00,
        supplier_is_approved=True,
        supplier_is_preferred=True,
        supplier_reliability_score=96.0,
        price_variance_pct=0.0,
        quantity=500
    )
    assert res.passed is True
    assert res.requires_escalation is True
    assert res.risk_level == "MEDIUM"

def test_guardrails_unapproved_supplier_blocks():
    # Unapproved supplier -> Policy breach, risk CRITICAL
    res = guardrails_engine.validate_purchase_order(
        total_amount=800.00,
        supplier_is_approved=False,
        supplier_is_preferred=False,
        supplier_reliability_score=65.0,
        price_variance_pct=0.0,
        quantity=100
    )
    assert res.passed is False
    assert res.requires_escalation is True
    assert res.risk_level == "CRITICAL"

def test_guardrails_price_variance_escalation():
    # Price variance +8% > 5% limit -> must escalate
    res = guardrails_engine.validate_purchase_order(
        total_amount=1200.00,
        supplier_is_approved=True,
        supplier_is_preferred=True,
        supplier_reliability_score=95.0,
        price_variance_pct=8.5,
        quantity=100
    )
    assert res.passed is True
    assert res.requires_escalation is True
    assert res.risk_level == "HIGH"
