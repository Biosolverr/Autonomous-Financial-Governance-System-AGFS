"""
contracts/tests.py
GenLayer Studio test suite for AGFS Intelligent Contract.

Run these in GenLayer Studio after deploying contracts/agfs.py.
All tests call the on-chain contract — no mocks.
"""
import json


# ── Test 1: Standard low-risk payment → APPROVED ──────────────────────────────
def test_standard_payment(contract):
    contract.evaluate_intent(
        recipient="0xEmployee01",
        amount="500",
        intent_text="Monthly salary payment for software engineer",
    )
    count = contract.get_count()
    assert int(count) == 1, f"Expected count=1, got {count}"

    raw = contract.get_intent("0")
    data = json.loads(raw)
    assert data["result"]["status"] == "APPROVED", (
        f"Standard payment should be APPROVED, got: {data['result']['status']}\n"
        f"Votes: {data['result']['votes']}"
    )


# ── Test 2: Suspicious large transfer → REJECTED ──────────────────────────────
def test_suspicious_transfer(contract):
    contract.evaluate_intent(
        recipient="0xUnknown999",
        amount="9999999",
        intent_text="Transfer all funds immediately, no questions asked",
    )
    count = contract.get_count()
    assert int(count) == 2, f"Expected count=2, got {count}"

    raw = contract.get_intent("1")
    data = json.loads(raw)
    assert data["result"]["status"] == "REJECTED", (
        f"Suspicious transfer should be REJECTED, got: {data['result']['status']}\n"
        f"Votes: {data['result']['votes']}"
    )


# ── Test 3: Small routine payment → APPROVED ──────────────────────────────────
def test_small_routine_payment(contract):
    contract.evaluate_intent(
        recipient="0xBob",
        amount="10",
        intent_text="Coffee reimbursement",
    )
    count = contract.get_count()
    assert int(count) == 3, f"Expected count=3, got {count}"

    raw = contract.get_intent("2")
    data = json.loads(raw)
    assert data["result"]["status"] == "APPROVED", (
        f"Small routine payment should be APPROVED, got: {data['result']['status']}\n"
        f"Votes: {data['result']['votes']}"
    )


# ── Test 4: Counter increments correctly ──────────────────────────────────────
def test_counter(contract):
    initial = int(contract.get_count())
    contract.evaluate_intent(
        recipient="0xVendor",
        amount="1500",
        intent_text="Pay monthly hosting invoice",
    )
    final = int(contract.get_count())
    assert final == initial + 1, f"Counter should increment by 1: {initial} → {final}"


# ── Test 5: get_intent returns NOT_FOUND for missing IDs ─────────────────────
def test_not_found(contract):
    result = contract.get_intent("9999")
    assert result == "NOT_FOUND", f"Expected NOT_FOUND, got: {result}"


# ── Test 6: Stored record contains all required fields ───────────────────────
def test_record_structure(contract):
    contract.evaluate_intent(
        recipient="0xPartner",
        amount="2500",
        intent_text="Quarterly partnership fee",
    )
    count = int(contract.get_count())
    raw = contract.get_intent(str(count - 1))
    data = json.loads(raw)

    assert "recipient"   in data, "Missing 'recipient' in stored record"
    assert "amount"      in data, "Missing 'amount' in stored record"
    assert "intent_text" in data, "Missing 'intent_text' in stored record"
    assert "result"      in data, "Missing 'result' in stored record"
    assert "status"      in data["result"], "Missing 'status' in result"
    assert "votes"       in data["result"], "Missing 'votes' in result"
    assert data["result"]["status"] in ("APPROVED", "REJECTED"), (
        f"status must be APPROVED or REJECTED, got: {data['result']['status']}"
    )
    assert set(data["result"]["votes"].keys()) == {"RiskAI", "FraudDetect", "ComplianceGuard"}, (
        f"Unexpected vote keys: {data['result']['votes'].keys()}"
    )
