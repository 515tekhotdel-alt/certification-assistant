"""
Отладочный файл для проверки DeepSeek API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")


def check_balance():
    """Проверка баланса DeepSeek API"""
    url = "https://api.deepseek.com/user/balance"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("\n💰 БАЛАНС DEEPSEEK API:")
        print(f"   Доступен: {data.get('is_available', False)}")
        for info in data.get("balance_infos", []):
            print(f"   Валюта: {info.get('currency')}")
            print(f"   Всего: {info.get('total_balance')}")
            print(f"   Подарочные: {info.get('granted_balance')}")
            print(f"   Пополнено: {info.get('topped_up_balance')}")
        return data
    else:
        print(f"❌ Ошибка проверки баланса: {response.status_code}")
        print(response.text)
        return None


def test_chat(query="пылесос"):
    """Тестовый запрос к DeepSeek"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Простой промпт
    prompt = f'Найди в списке товар, похожий на "{query}":\n0: Пылесос бытовой\n1: Чайник электрический\n2: Утюг\nОтветь только номером.'

    print(f"\n📤 ОТПРАВЛЯЕМ ЗАПРОС: {query}")
    print(f"   Промпт: {prompt[:100]}...")

    response = requests.post(
        url,
        headers=headers,
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 10
        },
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {})

        print(f"\n📥 ОТВЕТ: '{answer}'")
        print(f"\n📊 ТОКЕНЫ:")
        print(f"   Вход: {tokens.get('prompt_tokens', '?')}")
        print(f"   Выход: {tokens.get('completion_tokens', '?')}")
        print(f"   Всего: {tokens.get('total_tokens', '?')}")

        return answer
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    print("=" * 50)
    print("🔧 ОТЛАДКА DEEPSEEK API")
    print("=" * 50)

    # 1. Проверяем баланс
    balance = check_balance()

    # 2. Тестовый запрос
    if balance and balance.get("is_available"):
        test_chat("пылесос")
    else:
        print("\n⚠️ Баланс недоступен, пропускаем тестовый запрос.")
