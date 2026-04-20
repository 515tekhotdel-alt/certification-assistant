"""
Клиент для работы с DeepSeek API
"""

import sys
import re
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import requests
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL


class DeepSeekClient:
    """Класс для семантического поиска по наименованиям продукции через DeepSeek"""

    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.model = DEEPSEEK_MODEL
        self.base_url = "https://api.deepseek.com/v1/chat/completions"

    def find_best_match(self, query: str, products: list) -> dict:
        """
        Находит наиболее подходящее наименование продукции из списка.
        Использует двухэтапный подход: сначала отбираем кандидатов локально, потом уточняем через API.
        """
        # Этап 1: локальный отбор кандидатов (первые 5 по простому совпадению слов)
        candidates = self._get_candidates(query, products, top_n=5)

        if not candidates:
            return {"index": -1, "product": "", "confidence": 0.0}

        # Этап 2: уточнение через DeepSeek
        prompt = self._build_prompt(query, candidates)

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 10
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                return self._parse_response(answer, candidates, products)
            else:
                print(f"❌ DeepSeek API error: {response.status_code}")
                return {"index": -1, "product": "", "confidence": 0.0}

        except Exception as e:
            print(f"❌ DeepSeek request error: {e}")
            return {"index": -1, "product": "", "confidence": 0.0}

    def _get_candidates(self, query: str, products: list, top_n: int = 5) -> list:
        """Локальный отбор кандидатов по ключевым словам"""
        query_words = set(query.lower().split())
        scored = []

        for idx, product in enumerate(products):
            if not product:
                continue
            product_lower = str(product).lower()
            # Простой scoring: количество совпавших слов
            score = sum(1 for word in query_words if word in product_lower)
            if score > 0:
                scored.append((idx, product, score))

        # Сортируем по score и берём top_n
        scored.sort(key=lambda x: x[2], reverse=True)
        return [(idx, product) for idx, product, _ in scored[:top_n]]

    def _build_prompt(self, query: str, candidates: list) -> str:
        """Создаёт промпт для DeepSeek с малым числом кандидатов"""
        lines = []
        for i, (_, product) in enumerate(candidates):
            lines.append(f"{i}: {product}")

        prompt = f"""Найди товар, наиболее похожий на "{query}".

{chr(10).join(lines)}

Ответь только номером (0-{len(candidates) - 1})."""
        return prompt

    def _parse_response(self, answer: str, candidates: list, all_products: list) -> dict:
        """Парсит ответ DeepSeek"""
        match = re.search(r'[0-4]', answer)
        if match:
            candidate_idx = int(match.group())
            if 0 <= candidate_idx < len(candidates):
                original_idx = candidates[candidate_idx][0]
                return {
                    "index": original_idx,
                    "product": all_products[original_idx],
                    "confidence": 0.9
                }

        return {"index": -1, "product": "", "confidence": 0.0}

    def check_balance(self) -> dict:
        """Проверка баланса API"""
        url = "https://api.deepseek.com/user/balance"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {"is_available": False}


# Тестирование
if __name__ == "__main__":
    from src.database.loader import DataLoader

    loader = DataLoader()
    products = loader.get_product_names()

    client = DeepSeekClient()

    # Проверка баланса
    balance = client.check_balance()
    print(f"💰 Баланс доступен: {balance.get('is_available', False)}")

    # Тестовые запросы
    test_queries = ["пылесос", "чайник", "светильник", "ноутбук"]

    for query in test_queries:
        result = client.find_best_match(query, products)
        print(f"\n🔍 '{query}' → {result['product'][:60] if result['product'] else 'НЕ НАЙДЕНО'}...")