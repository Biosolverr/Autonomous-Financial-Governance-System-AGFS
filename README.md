# AGFS — Autonomous Financial Governance System

GenLayer Intelligent Contract + single-file HTML frontend.

A single LLM-based governance evaluation runs inside `gl.vm.run_nondet_unsafe`.
**Consensus is not simulated in application code.** It is provided by the
GenLayer network itself: every validator node independently re-executes the
governance evaluation (including its own LLM call), and the chain's
Optimistic Democracy protocol determines agreement before the transaction
finalizes. The frontend never imitates this — it submits directly to
studionet via `genlayer-js` and reads back whatever the network has finalized.

## Structure

```
contracts/agfs.py    ← GenLayer Intelligent Contract (deploy this in Studio)
contracts/tests.py   ← Studio test suite (6 tests)
frontend/index.html  ← Frontend (deploy to Vercel, calls contract directly)
frontend/tests.txt   ← Manual frontend test cases
```

## Deploy

### 1. Contract
- GenLayer Studio → new contract → paste `contracts/agfs.py` → Deploy
- Copy the contract address
- Run `contracts/tests.py` in Studio

### 2. Frontend
- Set `CONTRACT_ADDRESS` in `frontend/index.html`
- Push to GitHub → import in Vercel → Root Directory = `frontend`
- No build step, no backend, no mocked data — every read/write goes to studionet

## How it works

```
Browser
  └─ genlayer-js (esm.sh, no bundler)
       └─ writeContract("evaluate_intent", [recipient, amount, intent])
            └─ GenLayer contract
                 └─ gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
                      └─ gl.nondet.exec_prompt(...)  → {approve, score, reasoning}
                 → GenLayer network validators independently re-run
                   leader_fn and reach consensus (Optimistic Democracy)
                 → finalized result stored on-chain in TreeMap[str, str]
  └─ waitForTransactionReceipt
  └─ readContract("get_intent", [id]) → renders:
       - status badge, safety score
       - verdict card with score bar and one-sentence reasoning
       - tx hash as a clickable link to
         https://explorer-studio.genlayer.com/tx/<hash>
```

## Important architectural note

Earlier drafts of this contract simulated "3 AI agents voting" entirely
inside a single `leader_fn` — three separate LLM personas, manually
aggregated into a 2-of-3 majority by application code. That is **not**
GenLayer consensus; it's just three sequential LLM calls executed by
whichever single node happens to run the function. The current version
removes that simulation and relies on the real mechanism: GenLayer's
network-level validator consensus over one governance evaluation per
transaction.

## Result schema (stored on-chain per intent)

```json
{
  "recipient": "0xEmployee01",
  "amount": "500",
  "intent_text": "Pay monthly service invoice",
  "result": {
    "status": "APPROVED",
    "score": 88.0,
    "reasoning": "Routine, low-value payment with a clear description."
  }
}
```
