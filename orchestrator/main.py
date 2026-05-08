import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv

from agents.risk_agent import RiskAgent
from agents.fraud_agent import FraudAgent
from agents.compliance_agent import ComplianceAgent
from core.treasury_governance import TreasuryGovernance
from orchestrator.engine import MockConsensus

load_dotenv()

app = FastAPI(
    title="AGFS",
    description="Autonomous Financial Governance System"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://autonomous-financial-governance-sys-topaz.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/")
async def root():
    return {
        "status": "AGFS backend running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "agents": ["risk", "fraud", "compliance"]
    }


@app.post("/intent", response_model=IntentResponse)
async def process_intent(req: IntentRequest):

    intent_data = {
        "amount": req.amount,
        "recipient": req.recipient,
        "text": req.intent_text,
        "user_address": req.user_address
    }

    risk_agent = RiskAgent()
    fraud_agent = FraudAgent()
    compliance_agent = ComplianceAgent()

    risk_result = risk_agent.evaluate(intent_data)
    fraud_result = fraud_agent.evaluate(intent_data)
    compliance_result = compliance_agent.evaluate(intent_data)

    votes = [
        risk_result.get("approve", False),
        not fraud_result.get("fraud", True),
        compliance_result.get("approve", False)
    ]

    consensus = MockConsensus()

    consensus_result = consensus.run(
        votes,
        risk_result.get("score", 0.5)
    )

    approved = consensus_result.decision == "approve"

    if approved:

        treasury = TreasuryGovernance()

        tx_result = treasury.execute_transfer(
            req.recipient,
            req.amount,
            req.intent_text
        )

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
