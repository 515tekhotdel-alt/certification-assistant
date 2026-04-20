"""
Модуль поиска по базе сертификатов
"""

import pandas as pd
import sys
from pathlib import Path
from difflib import SequenceMatcher
import re

# Добавляем корень проекта в путь для импортов
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.database.loader import DataLoader
from src.config import COLUMN_MAPPING, SIMILARITY_THRESHOLD


class CertificateSearcher:
    """Класс для поиска подходящих сертификатов по запросу"""

    def __init__(self):
        self.loader = DataLoader()
        self.df = self.loader.get_dataframe()

    def search_by_product(self, query: str) -> list:
        """
        Ищет строки, похожие на запрос по наименованию продукции.
        Возвращает список словарей с результатами, отсортированных по схожести.
        """
        if self.df.empty:
            return []

        product_col = COLUMN_MAPPING["product"]
        results = []

        for idx, row in self.df.iterrows():
            product_name = str(row[product_col]) if pd.notna(row[product_col]) else ""
            similarity = SequenceMatcher(None,
                                         query.lower(),
                                         product_name.lower()).ratio()
            if similarity > 0.1:  # Минимальный порог для включения в результаты
                results.append({
                    "index": idx,
                    "similarity": similarity,
                    "product": product_name,
                    "row": row
                })

        # Сортировка по убыванию схожести
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results

    def filter_by_regulation(self, results: list, regulation: str) -> list:
        """Фильтрует результаты по техническому регламенту"""
        if not regulation:
            return results

        reg_col = COLUMN_MAPPING["regulations"]
        filtered = []
        for r in results:
            regulations = str(r["row"][reg_col]) if pd.notna(r["row"][reg_col]) else ""
            if regulation in regulations:
                filtered.append(r)
        return filtered

    def filter_by_tnved(self, results: list, tnved_4digits: str) -> list:
        """Фильтрует результаты по первым 4 цифрам ТНВЭД"""
        if not tnved_4digits or len(tnved_4digits) < 4:
            return results

        tnved_col = COLUMN_MAPPING["tnved"]
        filtered = []
        for r in results:
            tnved_value = str(r["row"][tnved_col]) if pd.notna(r["row"][tnved_col]) else ""
            # Извлекаем первые 4 цифры из строки (если они есть)
            import re
            match = re.search(r'(\d{4,})', tnved_value)
            if match:
                code = match.group(1)
                if code[:4] == tnved_4digits[:4]:
                    filtered.append(r)
        return filtered

    def get_best_match(self, results: list) -> dict or None:
        """Возвращает лучший результат с схожестью выше порога"""
        if not results:
            return None

        best = results[0]
        if best["similarity"] >= SIMILARITY_THRESHOLD:
            return best
        return None


# Тестирование
if __name__ == "__main__":
    searcher = CertificateSearcher()

    test_query = "пылесос"
    print(f"Поиск: '{test_query}'")

    results = searcher.search_by_product(test_query)
    print(f"Найдено результатов: {len(results)}")

    if results:
        print(f"\nТоп-3 совпадения:")
        for i, r in enumerate(results[:3]):
            print(f"  {i + 1}. [{r['similarity']:.2%}] {r['product'][:80]}...")
