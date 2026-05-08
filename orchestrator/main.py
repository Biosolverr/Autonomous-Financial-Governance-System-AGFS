import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging

from agents.risk_agent import RiskAgent
from agents.fraud_agent import FraudAgent
from agents.compliance_agent import ComplianceAgent
from core.treasury_governance import TreasuryGovernance
from orchestrator.engine import MockConsensus

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AGFS",
    description="Autonomous Financial Governance System",
    version="1.0.0"
)

# ── CORS: allow Vercel frontend (and local dev) ──────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # lock down to your Vercel domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ───────────────────────────────────────────────────────────────────

class IntentRequest(BaseModel):
    user_address: str
    amount: float
    recipient: str
    intent_text: str


class AgentDecision(BaseModel):
    agent: str
    approve: bool
    score: float
    flags: List[str]
    reasoning: str


class IntentResponse(BaseModel):
    status: str
    risk_score: float
    approved: bool
    reason: str
    agents: List[AgentDecision]
    consensus_confidence: float
    tx_hash: Optional[str] = None


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "AGFS - Autonomous Financial Governance System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "agents": ["risk", "fraud", "compliance"],
        "consensus": "MockConsensus (GenLayer-compatible)"
    }


@app.post("/intent", response_model=IntentResponse)
async def process_intent(req: IntentRequest):
    logger.info(f"Processing intent: amount={req.amount}, recipient={req.recipient}")

    intent_data = {
        "amount": req.amount,
        "recipient": req.recipient,
        "text": req.intent_text,
        "user_address": req.user_address,
    }

    # ── Run agents ────────────────────────────────────────────────────────────
    risk_agent = RiskAgent()
    fraud_agent = FraudAgent()
    compliance_agent = ComplianceAgent()

    risk_result       = risk_agent.evaluate(intent_data)
    fraud_result      = fraud_agent.evaluate(intent_data)
    compliance_result = compliance_agent.evaluate(intent_data)

    # ── Collect per-agent decisions ───────────────────────────────────────────
    agent_decisions = [
        AgentDecision(
            agent="RiskAI",
            approve=bool(risk_result.get("approve", False)),
            score=float(risk_result.get("score", 1.0)),
            flags=risk_result.get("flags", []),
            reasoning=risk_result.get("reasoning", ""),
        ),
        AgentDecision(
            agent="FraudDetect",
            approve=bool(fraud_result.get("approve", False)),
            score=float(fraud_result.get("score", 1.0)),
            flags=fraud_result.get("flags", []),
            reasoning=fraud_result.get("reasoning", ""),
        ),
        AgentDecision(
            agent="ComplianceGuard",
            approve=bool(compliance_result.get("approve", False)),
            score=float(compliance_result.get("score", 1.0)),
            flags=compliance_result.get("flags", []),
            reasoning=compliance_result.get("reasoning", ""),
        ),
    ]

    # ── Consensus ─────────────────────────────────────────────────────────────
    votes = [d.approve for d in agent_decisions]
    avg_risk_score = sum(d.score for d in agent_decisions) / len(agent_decisions)

    consensus = MockConsensus()
    consensus_result = consensus.run(votes, avg_risk_score)
    approved = consensus_result.decision == "approve"

    # ── Build reason string ───────────────────────────────────────────────────
    voted_yes = sum(1 for v in votes if v)
    reason = (
        f"{voted_yes}/{len(votes)} agents approved. "
        f"Confidence: {consensus_result.confidence:.0%}. "
        f"Risk: {risk_result.get('reasoning', '')}. "
        f"Fraud: {fraud_result.get('reasoning', '')}. "
        f"Compliance: {compliance_result.get('reasoning', '')}."
    )

    tx_hash: Optional[str] = None

    # ── Execute transfer if approved ──────────────────────────────────────────
    if approved:
        treasury = TreasuryGovernance()
        tx_result = treasury.execute_transfer(req.recipient, req.amount, req.intent_text)
        tx_hash = tx_result.get("tx_hash")
        reason += f" Tx: {tx_hash}"
        logger.info(f"Transfer executed: {tx_hash}")
    else:
        logger.info("Transfer rejected by consensus.")

    return IntentResponse(
        status="approved" if approved else "rejected",
        risk_score=avg_risk_score,
        approved=approved,
        reason=reason,
        agents=agent_decisions,
        consensus_confidence=float(consensus_result.confidence),
        tx_hash=tx_hash,
    )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    # Railway (and most PaaS) injects $PORT — always respect it
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting AGFS on port {port}")
    uvicorn.run("orchestrator.main:app", host="0.0.0.0", port=port, reload=False)
