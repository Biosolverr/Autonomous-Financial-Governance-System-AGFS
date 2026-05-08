import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock
from agents.risk_agent import RiskAgent
from agents.fraud_agent import FraudAgent
from agents.compliance_agent import ComplianceAgent

# Фикстура для мока Groq клиента
@pytest.fixture
def mock_groq():
    with patch('agents.base.Groq') as mock:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"score":0.2,"approve":true,"flags":[],"reasoning":"low risk"}'))]
        )
        mock.return_value = mock_instance
        yield mock

def test_risk_agent_evaluate(mock_groq):
    agent = RiskAgent()
    intent = {"amount": 500, "recipient": "0xABC", "text": "pay invoice"}
    result = agent.evaluate(intent)
    assert "score" in result
    assert 0 <= result["score"] <= 1
    assert "approve" in result

def test_fraud_agent_evaluate(mock_groq):
    agent = FraudAgent()
    intent = {"amount": 10000, "recipient": "0xScam", "text": "urgent transfer"}
    result = agent.evaluate(intent)
    assert "score" in result
    assert result["score"] >= 0

def test_compliance_agent_evaluate(mock_groq):
    agent = ComplianceAgent()
    intent = {"amount": 50000, "recipient": "0xSanctioned", "text": "donation"}
    result = agent.evaluate(intent)
    assert "approve" in result
