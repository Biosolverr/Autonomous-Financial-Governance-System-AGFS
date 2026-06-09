# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
contracts/agfs.py
Autonomous Financial Governance System — GenLayer Intelligent Contract.
"""
from genlayer import *


class AGFS(gl.Contract):
    intents: TreeMap[str, str]
    intent_count: u64

    def __init__(self):
        self.intents = TreeMap[str, str]()
        self.intent_count = u64(0)

    @gl.public.view
    def get_intent(self, intent_id: str) -> str:
        return self.intents.get(intent_id, "NOT_FOUND")

    @gl.public.view
    def get_count(self) -> u64:
        return self.intent_count

    @gl.public.write
    def evaluate_intent(self, recipient: str, amount: str, intent_text: str) -> None:

        def leader_fn() -> str:
            # Agent 1: RiskAI
            risk_raw = gl.nondet.exec_prompt(
                f"""You are a financial risk analyst for a crypto treasury.
Analyze this transaction and respond with ONLY one word: APPROVE or REJECT.
Approve if risk is low (routine payment, reasonable amount, clear description).
Reject if risk is high (suspicious recipient, huge amount, vague description).

Transaction:
- Recipient: {recipient}
- Amount: {amount} USD
- Description: {intent_text}"""
            )

            # Agent 2: FraudDetect
            fraud_raw = gl.nondet.exec_prompt(
                f"""You are a fraud detection specialist for a crypto treasury.
Analyze this transaction and respond with ONLY one word: APPROVE or REJECT.
Approve if no fraud signals. Reject if suspicious patterns detected.

Transaction:
- Recipient: {recipient}
- Amount: {amount} USD
- Description: {intent_text}"""
            )

            # Agent 3: ComplianceGuard
            compliance_raw = gl.nondet.exec_prompt(
                f"""You are a compliance officer for a crypto treasury.
Analyze this transaction and respond with ONLY one word: APPROVE or REJECT.
Approve if compliant with AML/KYC rules. Reject if policy violation detected.

Transaction:
- Recipient: {recipient}
- Amount: {amount} USD
- Description: {intent_text}"""
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

            votes = [parse(risk_raw), parse(fraud_raw), parse(compliance_raw)]
            approved = sum(1 for v in votes if v)
            return "APPROVED" if approved >= 2 else "REJECTED"

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            return leader_result.calldata in ("APPROVED", "REJECTED")

        status = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        intent_id = str(self.intent_count)
        self.intents[intent_id] = f"{recipient}|{amount}|{status}|{intent_text}"
        self.intent_count = u64(int(self.intent_count) + 1)
