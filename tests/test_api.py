from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is running"}

def test_predict_endpoint_success():
    payload = {
        "store_id": 1,
        "product_id": 1,
        "date": "2026-03-20",
        "recent_sales": [100.0, 105.0, 110.0, 95.0, 120.0, 125.0, 130.0]
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert data["store_id"] == 1
    assert data["product_id"] == 1

def test_reorder_decision_endpoint():
    payload = {
        "store_id": 1,
        "product_id": 1,
        "date": "2026-03-20",
        "recent_sales": [100.0, 105.0, 110.0, 95.0, 120.0, 125.0, 130.0],
        "lead_time": 2,
        "service_level_z": 1.65,
        "current_inventory": 500,
        "error_std": 20.5
    }
    response = client.post("/api/v1/reorder-decision", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reorder_point" in data
    assert "action" in data
    assert "recommended_reorder_qty" in data
