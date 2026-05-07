from consensus.engine import MockConsensus

def test_unanimous_approve():
    c = MockConsensus().run([True, True, True], 0.2)
    assert c.decision == "approve"
    assert c.quorum_met is True
    assert c.appeal_required is False

def test_unanimous_reject():
    c = MockConsensus().run([False, False, False], 0.9)
    assert c.decision == "reject"
    assert c.quorum_met is False

def test_split_vote_triggers_appeal():
    c = MockConsensus().run([True, True, False], 0.5)
    assert c.decision == "approve"
    assert c.appeal_required is True  # margin = 0.66 < 0.7

def test_majority_reject():
    c = MockConsensus().run([False, False, True], 0.8)
    assert c.decision == "reject"
