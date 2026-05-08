import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.engine import MockConsensus

def test_consensus_approve_2_1():
    consensus = MockConsensus()
    votes = [True, True, False]
    result = consensus.run(votes, risk_score=0.3)
    assert result.decision == "approve"
    assert result.quorum_met == True
    assert result.margin == 2/3

def test_consensus_reject_1_2():
    consensus = MockConsensus()
    votes = [True, False, False]
    result = consensus.run(votes, risk_score=0.8)
    assert result.decision == "reject"
    assert result.quorum_met == False

def test_consensus_all_approve():
    consensus = MockConsensus()
    votes = [True, True, True]
    result = consensus.run(votes, risk_score=0.1)
    assert result.decision == "approve"
    assert result.margin == 1.0

def test_consensus_all_reject():
    consensus = MockConsensus()
    votes = [False, False, False]
    result = consensus.run(votes, risk_score=0.9)
    assert result.decision == "reject"
    assert result.margin == 0.0

def test_consensus_appeal_required():
    consensus = MockConsensus()
    votes = [True, True, False]  # 2 approve, 1 reject -> margin 0.66 < 0.7
    result = consensus.run(votes, risk_score=0.5)
    # В engine.py appeal_required = margin < 0.7
    assert result.appeal_required == True
