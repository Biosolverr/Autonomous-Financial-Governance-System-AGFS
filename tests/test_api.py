import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from orchestrator.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_intent_approve():
    payload = {
        "user_address": "0x123",
        "amount": 500,
        "recipient": "0xABC",
        "intent_text": "pay invoice"
    }
    response = client.post("/intent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert data["approved"] in [True, False]
