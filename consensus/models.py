from pydantic import BaseModel
from typing import List, Optional

class ConsensusResult(BaseModel):
    decision: str  # "approve", "reject", "appeal"
    confidence: float
    margin: float
    quorum_met: bool
    appeal_required: bool
    details: Optional[dict] = None