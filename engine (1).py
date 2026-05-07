from policy.models import PolicyResult

class PolicyEngine:
    """
    Deterministic rule engine.
    AI agents NEVER reach here — only scores do.
    """
    def generate(self, amount: float, risk_score: float, consensus_margin: float) -> PolicyResult:
        # Base thresholds by amount
        if amount < 1000:
            threshold = 1
            delay = 0
        elif amount < 10000:
            threshold = 2
            delay = 86400       # 24h
        else:
            threshold = 3
            delay = 172800      # 48h

        # High risk → extra signer + extra delay
        if risk_score > 0.7:
            threshold += 1
            delay += 86400

        # Weak consensus → appeal window
        if consensus_margin < 0.7:
            delay += 43200      # +12h

        # Cap threshold at 3
        threshold = min(threshold, 3)

        return PolicyResult(
            threshold=threshold,
            time_delay=delay,
            max_single=amount * 1.5,
            rolling_window_sec=604800,  # 7-day cumulative tracking (smurf protection)
        )
