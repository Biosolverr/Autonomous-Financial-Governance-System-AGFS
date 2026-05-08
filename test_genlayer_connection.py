import os
from genlayer_py import create_client, create_account
from genlayer_py.chains import studionet, testnet_asimov

print("="*50)
print("AGFS: Тест подключения к реальному GenLayer SDK")
print("="*50)

network = os.getenv("GENLAYER_NETWORK", "studionet")
print(f"\n[1] Выбрана сеть: {network}")

if network == "studionet":
    chain = studionet
elif network == "testnet":
    chain = testnet_asimov
else:
    from genlayer_py.chains import localnet
    chain = localnet

try:
    print(f"\n[2] Подключение к {chain}...")
    client = create_client(chain=chain)
    print("    ✓ Клиент успешно создан!")

    print(f"\n[3] Создание аккаунта...")
    account = create_account()
    print(f"    ✓ Аккаунт создан: {account.address}")

    print(f"\n[4] Проверка баланса (запрос к сети)...")
    balance = client.get_balance(account.address)
    print(f"    ✓ Баланс аккаунта: {balance} wei")

    print("\n" + "="*50)
    print("✅ SDK успешно подключён к реальной сети GenLayer (studionet)!")
    print("="*50)

except Exception as e:
    print(f"\n❌ Ошибка подключения: {e}")
    print("\nПроверь интернет и настройки сети.")
