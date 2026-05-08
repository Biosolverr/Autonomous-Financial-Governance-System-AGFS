import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock
from agents.risk_agent import RiskAgent

def test_risk_score_by_amount():
    # Мокаем Groq, чтобы он возвращал скор в зависимости от суммы
    def mock_create(*args, **kwargs):
        messages = kwargs.get('messages', [])
        user_prompt = messages[1]['content'] if len(messages) > 1 else ""
        if "Amount: 50000" in user_prompt:
            content = '{"score":0.9,"approve":false,"flags":["large_amount"],"reasoning":"high amount"}'
        else:
            content = '{"score":0.2,"approve":true,"flags":[],"reasoning":"ok"}'
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=content))]
        return mock_response

    with patch('agents.base.Groq') as mock_groq:
        mock_client = MagicMock()
        mock_client.chat.completions.create = mock_create
        mock_groq.return_value = mock_client

        agent = RiskAgent()
        # малая сумма
        intent_small = {"amount": 500, "recipient": "0x123", "text": "invoice"}
        res_small = agent.evaluate(intent_small)
        assert res_small["score"] < 0.5

        # большая сумма
        intent_large = {"amount": 50000, "recipient": "0x123", "text": "investment"}
        res_large = agent.evaluate(intent_large)
        assert res_large["score"] > 0.8
