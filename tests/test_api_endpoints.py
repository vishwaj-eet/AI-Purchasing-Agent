def test_api_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "ProcurePulse" in data["app_name"]

def test_api_get_inventory(client):
    response = client.get("/api/inventory")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 7

def test_api_get_suppliers(client):
    response = client.get("/api/suppliers")
    assert response.status_code == 200
    suppliers = response.json()
    assert len(suppliers) >= 4

def test_api_workflow_run(client):
    response = client.post("/api/workflow/run", json={
        "trigger_type": "SCHEDULED_REPLENISHMENT"
    })
    assert response.status_code == 200
    data = response.json()
    assert "trace_id" in data
    assert data["status"] in ["COMPLETED", "ESCALATED_TO_HUMAN", "NO_REPLENISHMENT_NEEDED"]

def test_api_rag_search(client):
    response = client.post("/api/rag/search", json={
        "query": "financial approval limits",
        "top_k": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert data["total_found"] > 0
