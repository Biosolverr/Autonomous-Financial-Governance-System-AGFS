import os
from genlayer_py import create_client, create_account
from genlayer_py.chains import studionet

print("=== AGFS: Запрос тестовых токенов (faucet) ===")
client = create_client(chain=studionet)
account = create_account()
print(f"Аккаунт: {account.address}")

# Пытаемся запросить токены
try:
    # Метод может называться fund_account, request_funds и т.д.
    tx_hash = client.fund_account(account.address, amount=10**18)  # 1 токен
    print(f"✅ Транзакция фаусета отправлена: {tx_hash}")
    # Ждём подтверждения
    receipt = client.wait_for_transaction_receipt(tx_hash)
    print(f"✅ Баланс пополнен: {client.get_balance(account.address)} wei")
except AttributeError:
    print("⚠️ Метод fund_account не найден. Пробуем альтернативный способ...")
    # Возможно, через вызов контракта faucet
    # Здесь может потребоваться ручной запрос через браузер крана
