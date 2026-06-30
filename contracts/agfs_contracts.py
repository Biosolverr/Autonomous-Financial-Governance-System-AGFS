# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
contracts/agfs.py
Autonomous Financial Governance System — GenLayer Intelligent Contract.

A single LLM-based governance evaluation runs inside gl.vm.run_nondet_unsafe.
Consensus is NOT simulated in application code — it is provided by the
GenLayer network itself: every validator node independently re-executes
leader_fn (including its own LLM call) and the network's Optimistic
Democracy protocol determines agreement before the transaction finalizes.
This contract does not invent its own multi-agent voting layer on top of
that; it relies on the real consensus mechanism of the chain.
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
        """Return stored governance result for a given intent_id, or 'NOT_FOUND'."""
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

        A single governance prompt is sent to the LLM inside
        gl.vm.run_nondet_unsafe. GenLayer network validators each
        independently execute this function (including the LLM call)
        and reach consensus on the result via Optimistic Democracy —
        the chain's actual consensus mechanism, not a contract-level
        simulation of one.
        """

        _recipient = recipient
        _amount    = amount
        _intent    = intent_text

        def leader_fn() -> str:
            raw = gl.nondet.exec_prompt(
                f"You are an autonomous financial governance reviewer for a "
                f"crypto treasury. Evaluate the following transaction for "
                f"risk, fraud signals, and AML/compliance concerns in a "
                f"single combined judgement.\n\n"
                f"Transaction:\n"
                f"- Recipient: {_recipient}\n"
                f"- Amount: {_amount} USD\n"
                f"- Description: {_intent}\n\n"
                f"Respond with ONLY a JSON object, no markdown, no text outside JSON:\n"
                f'{{"approve": true/false, "score": 0-100, "reasoning": "one short sentence"}}\n'
                f"score = confidence that this transaction is SAFE "
                f"(100 = perfectly safe, 0 = extremely risky)."
            )

            try:
                if isinstance(raw, dict):
                    text = json.dumps(raw)
                else:
                    text = str(raw)
                text = text.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                    text = text.strip()
                obj = json.loads(text)
                approve   = bool(obj.get("approve", False))
                score     = float(obj.get("score", 0))
                score     = max(0.0, min(100.0, score))
                reasoning = str(obj.get("reasoning", ""))[:200]
            except Exception:
                approve, score, reasoning = False, 0.0, "parse_error: LLM response was not valid JSON"

            status = "APPROVED" if approve else "REJECTED"

            return json.dumps({
                "status": status,
                "score": score,
                "reasoning": reasoning,
            })

        def validator_fn(leader_result) -> bool:
            """
            Sanity check on the leader's output shape. Real agreement
            across nodes is handled by the GenLayer consensus protocol,
            not by this function — this only confirms the leader returned
            a well-formed governance verdict.
            """
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                data = json.loads(leader_result.calldata)
                return (
                    data.get("status") in ("APPROVED", "REJECTED")
                    and isinstance(data.get("score"), (int, float))
                    and isinstance(data.get("reasoning"), str)
                )
            except Exception:
                return False

        result_json = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        intent_id = str(int(self.intent_count))

        self.intents[intent_id] = json.dumps({
            "recipient":   _recipient,
            "amount":      _amount,
            "intent_text": _intent,
            "result":      json.loads(result_json),
        })

        self.intent_count = u64(int(self.intent_count) + 1)

