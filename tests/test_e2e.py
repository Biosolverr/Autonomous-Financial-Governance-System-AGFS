import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from orchestrator.main import app

client = TestClient(app)

@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
def test_e2e_full_flow():
    payload = {
        "user_address": "0xE2E",
        "amount": 750,
        "recipient": "0xVendor",
        "intent_text": "Payment for software license"
    }
    response = client.post("/intent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert isinstance(data["risk_score"], float)
    assert data["approved"] in [True, False]
    # Дополнительно проверим, что риск-скор в разумном диапазоне
    assert 0 <= data["risk_score"] <= 1
