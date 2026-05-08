import time
from genlayer_py import create_client, create_account
from genlayer_py.chains import studionet

client = create_client(chain=studionet)

import time
from genlayer_py import create_client, create_account
from genlayer_py.chains import studionet

client = create_client(chain=studionet)

import time
from genlayer_py import create_client, create_account
from genlayer_py.chains import studionet

client = create_client(chain=studionet)

import time
from genlayer_py import create_client, create_account
from genlayer_py.chains import studionet

client = create_client(chain=studionet)

account = create_account()
print(f"Создан аккаунт: {account.address}")

# Сохраняем только адрес (для отладки)
with open("account.txt", "w") as f:
    f.write(f"address={account.address}\n")

print("\nЗапрашиваем тестовые токены через faucet...")
tx_hash_bytes = client.fund_account(account.address, amount=10**18)
print(f"Транзакция отправлена. Хэш: {tx_hash_bytes.hex()}")

print("\nОжидаем поступления токенов (до 60 секунд)...")
for i in range(30):
    time.sleep(2)
    balance = client.get_balance(account.address)
    print(f"Попытка {i+1}: баланс = {balance} wei")
    if balance > 0:
        print(f"\n✅ Успех! Баланс пополнен до {balance} wei.")
        break
else:
    print("\n❌ Баланс не изменился за 60 секунд.")
