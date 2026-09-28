import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.tools.supplier_tools import evaluate_best_supplier
from app.rag.vector_store import vector_store
from app.memory.agent_memory import agent_memory

logger = logging.getLogger(__name__)

def evaluate_sourcing_options(
    db: Session,
    trace_id: str,
    candidates: List[Dict[str, Any]]
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Evaluates supplier options for replenishment candidates, queries RAG knowledge base
    for contract terms, and selects optimal supplier.
    """
    sourcing_recommendations = []
    rag_snippets = []

    for cand in candidates:
        sku = cand["sku"]
        requested_qty = cand["recommended_quantity"]

        # 1. Query RAG vector store for procurement policy & supplier MSAs
        rag_results = vector_store.search(query=f"Supplier terms for {sku} {cand['category']} pricing SLA", top_k=2)
        citations = []
        for r in rag_results:
            citations.append({
                "doc_id": r["doc_id"],
                "title": r["title"],
                "snippet": r["content"][:200] + "...",
                "score": r["similarity_score"]
            })
            rag_snippets.extend(citations)

        # 2. Find and evaluate best supplier
        best_supplier = evaluate_best_supplier(db, sku, requested_qty)
        if not best_supplier:
            logger.warning(f"No approved supplier found for {sku}")
            continue

        # Calculate price variance against product benchmark cost
        benchmark_cost = cand.get("unit_cost", best_supplier["effective_unit_price"])
        if benchmark_cost > 0:
            price_variance_pct = round(((best_supplier["effective_unit_price"] - benchmark_cost) / benchmark_cost) * 100.0, 2)
        else:
            price_variance_pct = 0.0

        recommendation = {
            "sku": sku,
            "product_name": cand["name"],
            "supplier_id": best_supplier["supplier_id"],
            "supplier_code": best_supplier["supplier_code"],
            "supplier_name": best_supplier["supplier_name"],
            "contact_email": best_supplier["contact_email"],
            "order_quantity": best_supplier["adjusted_order_qty"],
            "unit_price": best_supplier["effective_unit_price"],
            "total_cost": best_supplier["total_estimated_cost"],
            "lead_time_days": best_supplier["lead_time_days"],
            "is_preferred": best_supplier["is_preferred"],
            "reliability_score": best_supplier["reliability_score"],
            "price_variance_pct": price_variance_pct,
            "rationale": best_supplier["selection_reason"],
            "rag_citations": citations
        }
        sourcing_recommendations.append(recommendation)

    agent_memory.log_trace(
        db=db,
        trace_id=trace_id,
        agent_name="SourcingNegotiationAgent",
        step_name="evaluate_suppliers_and_contracts",
        event_type="SOURCING_EVALUATED",
        input_payload={"candidates_count": len(candidates)},
        output_payload={"recommendations_count": len(sourcing_recommendations), "sourcing": sourcing_recommendations},
        status="SUCCESS"
    )

    return sourcing_recommendations, rag_snippets
