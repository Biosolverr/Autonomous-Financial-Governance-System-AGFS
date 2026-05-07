import hashlib
from safe.models import SafePayload
from config.settings import settings

def build_safe_tx(
    intent_hash: str,
    recipient: str,
    amount: float,
    policy,
    nonce: int,
    timestamp: int,
) -> SafePayload:
    # Bind all parameters — audit trail + replay protection
    payload_str = f"{intent_hash}|{recipient}|{amount}|{nonce}|{timestamp}"
    policy_hash = hashlib.sha256(payload_str.encode()).hexdigest()

    return SafePayload(
        to=recipient,
        value=amount,
        nonce=nonce,
        safe_threshold=policy.threshold,
        execution_delay_sec=policy.time_delay,
        timestamp=timestamp,
        policy_hash=policy_hash,
        intent_hash=intent_hash,
        chain_id=settings.CHAIN_ID,
        eip712_domain={
            "name": "AutonomousTreasury",
            "version": "1",
            "chainId": settings.CHAIN_ID,
            "verifyingContract": settings.SAFE_CONTRACT_ADDRESS,
        },
    )
