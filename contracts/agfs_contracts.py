# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
contracts/agfs.py
Autonomous Financial Governance System — GenLayer Intelligent Contract.

Three AI agents (RiskAI, FraudDetect, ComplianceGuard) evaluate every
transaction in parallel inside gl.vm.run_nondet_unsafe, reaching consensus
via 2-of-3 majority vote before the result is committed on-chain.
"""
import json
from genlayer import *


class AGFS(gl.Contract):
    # State: intent_id (str) -> JSON result string
    intents: TreeMap[str, str]
    # Monotonic counter used as intent ID
    intent_count: u64

    def __init__(self) -> None:
        pass  # State variables are initialised by the runtime from annotations

    # ── Views ──────────────────────────────────────────────────────────────────

    @gl.public.view
    def get_intent(self, intent_id: str) -> str:
        """Return stored result for a given intent_id, or 'NOT_FOUND'."""
        return self.intents.get(intent_id, "NOT_FOUND")

    @gl.public.view
    def get_count(self) -> u64:
        """Return total number of evaluated intents."""
        return self.intent_count

    # ── Writes ─────────────────────────────────────────────────────────────────

    @gl.public.write
    def evaluate_intent(self, recipient: str, amount: str, intent_text: str) -> None:
        """
        Submit a transaction for AI governance.
        Three independent AI agents vote; 2-of-3 majority decides APPROVED / REJECTED.
        Result is stored on-chain and can be retrieved via get_intent().
        """

        # Capture args in local vars so closures can access them without `self`
        _recipient  = recipient
        _amount     = amount
        _intent     = intent_text

        def leader_fn() -> str:
            # ── Agent 1: RiskAI ────────────────────────────────────────────
            risk_raw = gl.nondet.exec_prompt(
                f"You are a financial risk analyst for a crypto treasury.\n"
                f"Analyze this transaction. Respond with ONLY one word: APPROVE or REJECT.\n"
                f"Approve if risk is low (routine payment, reasonable amount, clear description).\n"
                f"Reject if risk is high (suspicious recipient, huge amount, vague description).\n\n"
                f"Transaction:\n"
                f"- Recipient: {_recipient}\n"
                f"- Amount: {_amount} USD\n"
                f"- Description: {_intent}"
            )

            # ── Agent 2: FraudDetect ───────────────────────────────────────
            fraud_raw = gl.nondet.exec_prompt(
                f"You are a fraud detection specialist for a crypto treasury.\n"
                f"Analyze this transaction. Respond with ONLY one word: APPROVE or REJECT.\n"
                f"Approve if no fraud signals present. Reject if suspicious patterns detected.\n\n"
                f"Transaction:\n"
                f"- Recipient: {_recipient}\n"
                f"- Amount: {_amount} USD\n"
                f"- Description: {_intent}"
            )

            # ── Agent 3: ComplianceGuard ───────────────────────────────────
            compliance_raw = gl.nondet.exec_prompt(
                f"You are a compliance officer for a crypto treasury.\n"
                f"Analyze this transaction. Respond with ONLY one word: APPROVE or REJECT.\n"
                f"Approve if compliant with AML/KYC rules. Reject if policy violation detected.\n\n"
                f"Transaction:\n"
                f"- Recipient: {_recipient}\n"
                f"- Amount: {_amount} USD\n"
                f"- Description: {_intent}"
            )

            def parse(raw) -> bool:
                try:
                    if isinstance(raw, dict):
                        v = str(list(raw.values())[0]).strip().upper()
                    else:
                        v = str(raw).strip().upper()
                    return "APPROVE" in v
                except Exception:
                    return False

            risk_vote       = parse(risk_raw)
            fraud_vote      = parse(fraud_raw)
            compliance_vote = parse(compliance_raw)

            votes    = [risk_vote, fraud_vote, compliance_vote]
            approved = sum(1 for v in votes if v)
            status   = "APPROVED" if approved >= 2 else "REJECTED"

            return json.dumps({
                "status": status,
                "votes": {
                    "RiskAI":         "APPROVE" if risk_vote       else "REJECT",
                    "FraudDetect":    "APPROVE" if fraud_vote      else "REJECT",
                    "ComplianceGuard":"APPROVE" if compliance_vote else "REJECT",
                },
                "majority": approved,
            })

        def validator_fn(leader_result) -> bool:
            """
            Validator just checks that the leader produced a well-formed result
            with a valid status field.  The LLM calls run independently on
            each validator node — GenLayer's consensus mechanism handles
            equivocation via Optimistic Democracy.
            """
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                data = json.loads(leader_result.calldata)
                return data.get("status") in ("APPROVED", "REJECTED")
            except Exception:
                return False

        result_json = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        intent_id = str(int(self.intent_count))

        # Store compact record: recipient|amount|result_json
        self.intents[intent_id] = json.dumps({
            "recipient":   _recipient,
            "amount":      _amount,
            "intent_text": _intent,
            "result":      json.loads(result_json),
        })

        self.intent_count = u64(int(self.intent_count) + 1)
