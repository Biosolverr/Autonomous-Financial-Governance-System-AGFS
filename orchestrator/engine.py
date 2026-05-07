from consensus.models import ConsensusResult

class MockConsensus:
    """
    Simulates GenLayer Optimistic Democracy.
    Later: replace with real GenLayer RPC call.
    """
    def run(self, votes: list[bool], risk_score: float) -> ConsensusResult:
        approve = sum(votes)
        total = len(votes)
        margin = approve / total if total > 0 else 0

        appeal = margin < 0.7
        confidence = margin
        decision = "approve" if approve > total / 2 else "reject"

        return ConsensusResult(
            decision=decision,
            confidence=confidence,
            margin=margin,
            quorum_met=approve > total / 2,
            appeal_required=appeal,
        )