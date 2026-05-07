import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv

from agents.risk_agent import RiskAgent
from agents.fraud_agent import FraudAgent
from agents.compliance_agent import ComplianceAgent
from core.treasury_governance import TreasuryGovernance
from orchestrator.engine import MockConsensus

load_dotenv()

app = FastAPI(title="AGFS", description="Autonomous Financial Governance System")

class IntentRequest(BaseModel):
    user_address: str
    amount: float
    recipient: str
    intent_text: str

class IntentResponse(BaseModel):
    status: str
    risk_score: float
    approved: bool
    reason: str

@app.post("/intent", response_model=IntentResponse)
async def process_intent(req: IntentRequest):
    # Подготовка данных для агентов
    intent_data = {
        "amount": req.amount,
        "recipient": req.recipient,
        "text": req.intent_text,
        "user_address": req.user_address
    }
    
    # Запуск агентов (каждый имеет метод evaluate)
    risk_agent = RiskAgent()
    fraud_agent = FraudAgent()
    compliance_agent = ComplianceAgent()
    
    risk_result = risk_agent.evaluate(intent_data)
    fraud_result = fraud_agent.evaluate(intent_data)
    compliance_result = compliance_agent.evaluate(intent_data)
    
    # Голосование (имитация 3 валидаторов)
    votes = [
        risk_result.get("approve", False),
        not fraud_result.get("fraud", True),
        compliance_result.get("approve", False)
    ]
    
    # Консенсус
    consensus = MockConsensus()
    consensus_result = consensus.run(votes, risk_result.get("score", 0.5))
    
    approved = consensus_result.decision == "approve"
    
    # Исполнение
    if approved:
        treasury = TreasuryGovernance()
        tx_result = treasury.execute_transfer(req.recipient, req.amount, req.intent_text)
        return IntentResponse(
            status="approved",
            risk_score=risk_result.get("score", 0.5),
            approved=True,
            reason=f"Consensus: {consensus_result.decision}. Tx: {tx_result.get('tx_hash', 'pending')}"
        )
    else:
        return IntentResponse(
            status="rejected",
            risk_score=risk_result.get("score", 0.5),
            approved=False,
            reason=f"Consensus: {consensus_result.decision}. Risk: {risk_result.get('reasoning', 'High risk')}"
        )

@app.get("/health")
def health():
    return {"status": "ok", "agents": ["risk", "fraud", "compliance"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)