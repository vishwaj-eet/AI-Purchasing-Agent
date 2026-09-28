from app.rag.vector_store import vector_store

def test_rag_retrieval_procurement_policy():
    results = vector_store.search("What is the financial threshold for autonomous purchase orders?")
    assert len(results) > 0
    top = results[0]
    assert "SOP-PROC-001" in top["doc_id"] or "Procurement Policy" in top["title"]
    assert top["similarity_score"] > 0.4

def test_rag_retrieval_supplier_msa():
    results = vector_store.search("Apex Electronics lead time and minimum order quantity")
    assert len(results) > 0
    top = results[0]
    assert "Apex" in top["title"]
    assert "MSA" in top["doc_id"]

def test_rag_dynamic_document_indexing():
    vector_store.add_document(
        doc_id="TEST-SOP-999",
        title="Custom Hazardous Materials Handling SOP",
        category="COMPLIANCE",
        content="All lithium ion battery shipments must be classified as UN3480 Class 9 dangerous goods."
    )

    res = vector_store.search("lithium ion battery UN3480")
    assert len(res) > 0
    assert any(r["doc_id"] == "TEST-SOP-999" for r in res)
