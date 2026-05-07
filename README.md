Autonomous Financial Governance System (AGFS)
A decentralized AI-powered transaction governance system built on GenLayer + Safe multisig.

Architecture
USER INTENT
    ↓
ORCHESTRATOR (FastAPI)
    ↓
AI AGENTS (Risk + Fraud + Finance) — powered by Groq (free)
    ↓
MOCK GENLAYER CONSENSUS (majority vote)
    ↓
POLICY ENGINE (threshold, delay, limits)
    ↓
SAFE TX BUILDER
    ↓
ON-CHAIN EXECUTION
Stack
GenLayer — Intelligent Contracts (Python + LLM)
Safe — multisig custody layer
Groq API — free LLM inference (llama3-8b)
FastAPI — orchestrator backend
Python 3.11+
Quickstart
# 1. Clone and install
pip install -r requirements.txt

# 2. Set your free Groq API key (groq.com)
cp .env.example .env
# edit .env and paste your GROQ_API_KEY

# 3. Run orchestrator
uvicorn orchestrator.main:app --reload

# 4. Send a transaction intent
curl -X POST http://localhost:8000/intent \
  -H "Content-Type: application/json" \
  -d '{"to": "0xABC...", "amount": 5000, "description": "Pay contractor"}'
Project Structure
agfs/
├── contracts/          # GenLayer Intelligent Contracts
├── agents/             # AI analysis agents (Risk, Fraud, Finance)
├── core/               # Consensus engine + Policy engine
├── orchestrator/       # FastAPI coordinator
├── safe/               # Safe transaction builder
└── tests/              # pytest test suite
Security Model
AI agents never execute transactions — they only recommend
All money flows through Safe multisig with deterministic rules
AI outputs are bound to tx hash + timestamp (replay protection)
Validator diversity: 3 independent agents with different prompts
Known Limitations (MVP)
Mock GenLayer consensus (real GenLayer integration planned)
No persistent state between runs
Groq free tier rate limits (~30 req/min)
