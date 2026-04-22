
"""
Быстрая проверка баланса DeepSeek API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not API_KEY:
    print("❌ DEEPSEEK_API_KEY не найден в .env")
    exit(1)

url = "https://api.deepseek.com/user/balance"
headers = {"Authorization": f"Bearer {API_KEY}"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("\n💰 БАЛАНС DEEPSEEK API")
    print("-" * 30)
    print(f"Доступен: {data.get('is_available', False)}")
    for info in data.get("balance_infos", []):
        print(f"Валюта: {info.get('currency', 'USD')}")
        total = info.get('total_balance', '0')
        granted = info.get('granted_balance', '0')
        topped = info.get('topped_up_balance', '0')
        print(f"Всего: {total}")
        print(f"Подарочные: {granted}")
        print(f"Пополнено: {topped}")
else:
    print(f"❌ Ошибка: {response.status_code}")
    print(response.text)