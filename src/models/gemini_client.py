"""
Клиент для работы с Gemini API
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import google.generativeai as genai
from src.config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiClient:
    """Класс для семантического поиска по наименованиям продукции"""

    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    def find_best_match(self, query: str, products: list, max_items: int = 100) -> dict:
        """
        Находит наиболее подходящее наименование продукции из списка.

        Args:
            query: поисковый запрос пользователя
            products: список наименований продукции из базы
            max_items: максимальное количество вариантов для отправки в Gemini

        Returns:
            dict с результатом: {"index": int, "product": str, "confidence": float}
        """
        # Ограничиваем количество для API
        sample_products = products[:max_items]

        prompt = self._build_prompt(query, sample_products)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=200
                )
            )
            return self._parse_response(response.text, products)
        except Exception as e:
            print(f"❌ Ошибка Gemini API: {e}")
            return {"index": -1, "product": "", "confidence": 0.0, "error": str(e)}

    def _build_prompt(self, query: str, products: list) -> str:
        """Создаёт промпт для Gemini"""
        products_text = ""
        for i, p in enumerate(products[:50]):  # Ещё сильнее ограничиваем для промпта
            if p and len(str(p)) > 5:
                products_text += f"{i}: {p}\n"

        prompt = f"""
Ты — помощник для подбора стандартов сертификации.

Пользователь ищет: "{query}"

Вот список возможных категорий продукции (с индексами):
{products_text}

Найди индекс категории, которая НАИБОЛЕЕ СООТВЕТСТВУЕТ запросу пользователя.
Учитывай синонимы и категории товаров.

Верни ТОЛЬКО JSON в формате:
{{"index": номер_индекса, "product": "точное_название_из_списка", "confidence": число_от_0_до_1}}

Если подходящей категории нет, верни: {{"index": -1, "product": "", "confidence": 0}}
"""
        return prompt

    def _parse_response(self, text: str, products: list) -> dict:
        """Парсит ответ Gemini"""
        import json
        import re

        # Извлекаем JSON из ответа
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return {
                    "index": result.get("index", -1),
                    "product": result.get("product", ""),
                    "confidence": result.get("confidence", 0.0)
                }
            except json.JSONDecodeError:
                pass

        return {"index": -1, "product": "", "confidence": 0.0}


# Тестирование
if __name__ == "__main__":
    from src.database.loader import DataLoader

    loader = DataLoader()
    products = loader.get_product_names()

    client = GeminiClient()
    result = client.find_best_match("пылесос моющий", products)

    print(f"Запрос: 'пылесос моющий'")
    print(f"Результат: {result}")
