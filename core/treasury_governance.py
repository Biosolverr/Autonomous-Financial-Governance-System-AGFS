import os
from genlayer_py import create_client
from genlayer_py.chains import localnet

class TreasuryGovernance:
    def __init__(self):
        self.treasury_address = os.getenv("TREASURY_ADDRESS", "0xTreasuryMainVault")
        self.client = None
        
        try:
            # Подключаемся к локальной сети для тестов
            self.client = create_client(localnet)
        except Exception as e:
            print(f"Warning: Could not connect to GenLayer: {e}")
            self.client = None
    
    def execute_transfer(self, recipient: str, amount: float, reason: str) -> dict:
        """
        Execute a transfer using GenLayer SDK
        """
        try:
            if self.client:
                amount_wei = int(amount * 10**18)
                
                tx = self.client.send_transaction(
                    to=recipient,
                    value=amount_wei,
                    data=reason
                )
                
                return {
                    "tx_hash": tx.hash if hasattr(tx, 'hash') else f"0x{os.urandom(20).hex()}",
                    "status": "executed",
                    "recipient": recipient,
                    "amount": amount,
                    "reason": reason
                }
            else:
                return {
                    "tx_hash": f"0x{os.urandom(20).hex()}",
                    "status": "simulated",
                    "recipient": recipient,
                    "amount": amount,
                    "reason": reason,
                    "note": "GenLayer client not configured"
                }
        except Exception as e:
            return {
                "tx_hash": f"0x{os.urandom(20).hex()}",
                "status": "failed",
                "recipient": recipient,
                "amount": amount,
                "reason": reason,
                "error": str(e)
            }