"""
Клиент для работы с DeepSeek API
Задача: найти ВСЕ строки в таблице, соответствующие запросу
"""

import sys
import json
import re
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import requests
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL


class DeepSeekClient:
    """Класс для семантического поиска релевантных строк по запросу"""

    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.model = DEEPSEEK_MODEL
        self.base_url = "https://api.deepseek.com/v1/chat/completions"

    def find_relevant_indices(self, query: str, products: list) -> list:
        """
        Находит ВСЕ индексы продуктов, соответствующих запросу.
        Использует локальный отбор 30 кандидатов + DeepSeek.
        """
        candidates = self._get_candidates_by_keywords(query, products, top_n=30)

        if not candidates:
            return []

        prompt = self._build_batch_prompt(query, candidates)

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
                    "max_tokens": 200
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                tokens = result.get("usage", {})
                print(
                    f"🔵 [DEEPSEEK] Токенов: вход={tokens.get('prompt_tokens')}, выход={tokens.get('completion_tokens')}")
                return self._parse_batch_response(answer, candidates)
            else:
                print(f"❌ DeepSeek API error: {response.status_code} - {response.text[:200]}")
                return []

        except Exception as e:
            print(f"❌ DeepSeek request error: {e}")
            return []

    def find_in_full_base(self, query: str, products: list, progress_bar=None, status_text=None) -> list:
        """
        Отправляет в DeepSeek ВСЕ названия продукции для поиска.
        С таймаутом 60 секунд.
        """

        import time

        batch_size = 500
        timeout = 90  # секунд
        start_time = time.time()

        total_batches = (len(products) - 1) // batch_size + 1
        print(f"\n🔵 [DEEPSEEK FULL] Запрос: '{query}'")
        print(f"🔵 [DEEPSEEK FULL] Всего продуктов: {len(products)}")
        print(f"🔵 [DEEPSEEK FULL] Всего батчей: {total_batches}")

        all_results = []

        for i in range(0, len(products), batch_size):
            # Таймаут
            if time.time() - start_time > timeout:
                print(f"⏰ Таймаут ({timeout}с), найдено: {len(all_results)}")
                break

            batch = products[i:i + batch_size]
            candidates = [(i + j, p) for j, p in enumerate(batch)]
            prompt = self._build_batch_prompt(query, candidates)

            batch_num = i // batch_size + 1
            print(f"🔵 [DEEPSEEK FULL] Батч {batch_num}/{total_batches}...")
            if progress_bar is not None and status_text is not None:
                progress = min((i + len(batch)) / len(products), 1.0)
                progress_bar.progress(progress)
                status_text.text(f"🔵 Умный поиск: {i + len(batch)} из {len(products)}")

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
                        "max_tokens": 500
                    },
                    timeout=45
                )

                if response.status_code == 200:
                    result = response.json()
                    answer = result["choices"][0]["message"]["content"]
                    tokens = result.get("usage", {})
                    print(
                        f"🔵 [DEEPSEEK FULL] Батч {batch_num}: вход={tokens.get('prompt_tokens')}, выход={tokens.get('completion_tokens')}")
                    batch_results = self._parse_batch_response(answer, candidates)
                    all_results.extend(batch_results)
                else:
                    print(f"❌ DeepSeek API error: {response.status_code}")

            except Exception as e:
                print(f"❌ DeepSeek request error: {e}")

        print(f"🔵 [DEEPSEEK FULL] Всего найдено: {len(all_results)}")
        return all_results

    def _get_candidates_by_keywords(self, query: str, products: list, top_n: int = 30) -> list:
        """Быстрый локальный отбор по ключевым словам"""
        query_words = set(query.lower().split())
        scored = []

        for idx, product in enumerate(products):
            if not product:
                continue
            product_lower = str(product).lower()
            score = sum(1 for word in query_words if word in product_lower)
            if score > 0:
                scored.append((idx, product, score))

        scored.sort(key=lambda x: x[2], reverse=True)
        return [(idx, product) for idx, product, _ in scored[:top_n]]

    def _build_batch_prompt(self, query: str, candidates: list) -> str:
        """Промпт для отбора всех подходящих вариантов"""
        lines = []
        for i, (_, product) in enumerate(candidates):
            short_product = product[:80] + "..." if len(product) > 80 else product
            lines.append(f"{i}: {short_product}")

        prompt = f"""Найди ВСЕ товары из списка, которые соответствуют запросу: "{query}".

Список:
{chr(10).join(lines)}

Верни ТОЛЬКО JSON-массив с номерами подходящих товаров.
Пример ответа: [0, 3, 7]

Если ничего не подходит, верни: []"""
        return prompt

    def _parse_batch_response(self, answer: str, candidates: list) -> list:
        """Парсит ответ с массивом индексов"""
        match = re.search(r'\[.*?\]', answer, re.DOTALL)
        if match:
            try:
                indices = json.loads(match.group())
                results = []
                for i in indices:
                    if isinstance(i, int) and 0 <= i < len(candidates):
                        original_idx = candidates[i][0]
                        results.append({
                            "index": original_idx,
                            "product": candidates[i][1],
                            "confidence": 0.9
                        })
                return results
            except json.JSONDecodeError:
                pass

        numbers = re.findall(r'\b\d+\b', answer)
        results = []
        for num in numbers[:10]:
            i = int(num)
            if 0 <= i < len(candidates):
                original_idx = candidates[i][0]
                results.append({
                    "index": original_idx,
                    "product": candidates[i][1],
                    "confidence": 0.8
                })

        return results

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