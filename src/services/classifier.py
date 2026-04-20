"""
Основной сервис классификации — объединяет поиск по базе и DeepSeek
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
from src.database.searcher import CertificateSearcher
from src.models.deepseek_client import DeepSeekClient
from src.config import COLUMN_MAPPING, SIMILARITY_THRESHOLD


class CertificationAssistant:
    """Основной класс помощника эксперта по сертификации"""

    def __init__(self):
        self.searcher = CertificateSearcher()
        self.deepseek = DeepSeekClient()
        self.df = self.searcher.df

    def process_query(self, product_query: str, regulation: str = "", tnved: str = "") -> dict:
        """
        Обрабатывает запрос эксперта.

        Args:
            product_query: описание продукции
            regulation: технический регламент (опционально)
            tnved: первые 4 цифры ТНВЭД (опционально)

        Returns:
            dict с результатом поиска
        """
        # Шаг 1: локальный поиск по базе (SequenceMatcher)
        local_results = self.searcher.search_by_product(product_query)

        # Шаг 2: применяем фильтры
        if regulation:
            local_results = self.searcher.filter_by_regulation(local_results, regulation)
        if tnved:
            local_results = self.searcher.filter_by_tnved(local_results, tnved)

        # Шаг 3: проверяем, есть ли точное совпадение
        best_local = self.searcher.get_best_match(local_results)

        if best_local and best_local["similarity"] >= SIMILARITY_THRESHOLD:
            # Найден точный прецедент
            return self._format_result(best_local, source="precedent")

        # Шаг 4: точного совпадения нет — используем DeepSeek
        if local_results:
            # Если есть хоть какие-то кандидаты — уточняем через DeepSeek
            products = [r["product"] for r in local_results[:10]]
            ai_match = self.deepseek.find_best_match(product_query, products)

            if ai_match["index"] >= 0:
                # Нашли соответствие среди кандидатов
                matched_product = ai_match["product"]
                # Ищем полную строку в local_results
                for r in local_results:
                    if r["product"] == matched_product:
                        return self._format_result(r, source="ai_assisted")
        else:
            # Кандидатов нет — ищем по всем продуктам через DeepSeek
            all_products = self.searcher.loader.get_product_names()
            ai_match = self.deepseek.find_best_match(product_query, all_products)
            if ai_match["index"] >= 0:
                row = self.df.iloc[ai_match["index"]]
                result = {
                    "index": ai_match["index"],
                    "similarity": ai_match["confidence"],
                    "product": ai_match["product"],
                    "row": row
                }
                return self._format_result(result, source="ai_only")

        # Шаг 5: ничего не нашли
        return {
            "found": False,
            "source": "none",
            "message": "По вашему запросу ничего не найдено. Попробуйте изменить описание продукции."
        }

    def _format_result(self, result: dict, source: str) -> dict:
        """Форматирует результат для вывода"""
        row = result["row"]

        # Парсим стандарты
        standards_des = str(row[COLUMN_MAPPING["standards_designation"]]) if pd.notna(
            row[COLUMN_MAPPING["standards_designation"]]) else ""
        standards_name = str(row[COLUMN_MAPPING["standards_name"]]) if pd.notna(
            row[COLUMN_MAPPING["standards_name"]]) else ""

        des_list = [s.strip() for s in standards_des.split(";") if s.strip()]
        name_list = [s.strip() for s in standards_name.split(";") if s.strip()]

        # Объединяем обозначения и названия
        standards = []
        for i, des in enumerate(des_list):
            name = name_list[i] if i < len(name_list) else ""
            standards.append({"designation": des, "name": name})

        return {
            "found": True,
            "source": source,
            "product": result["product"],
            "similarity": result["similarity"],
            "certificate_number": str(row[COLUMN_MAPPING["number"]]) if pd.notna(row[COLUMN_MAPPING["number"]]) else "",
            "certificate_date": str(row[COLUMN_MAPPING["date"]]) if pd.notna(row[COLUMN_MAPPING["date"]]) else "",
            "regulations": str(row[COLUMN_MAPPING["regulations"]]) if pd.notna(
                row[COLUMN_MAPPING["regulations"]]) else "",
            "tnved": str(row[COLUMN_MAPPING["tnved"]]) if pd.notna(row[COLUMN_MAPPING["tnved"]]) else "",
            "standards": standards,
            "standards_count": len(standards)
        }

    def get_source_label(self, source: str) -> tuple:
        """Возвращает метку и эмодзи для источника"""
        labels = {
            "precedent": ("✅ ПРЕЦЕДЕНТ", "success"),
            "ai_assisted": ("🤖 НАЙДЕНО ИИ (среди похожих)", "info"),
            "ai_only": ("⚠️ ПРЕДПОЛОЖЕНИЕ ИИ (требуется проверка)", "warning"),
            "none": ("❌ НЕ НАЙДЕНО", "error")
        }
        return labels.get(source, ("", "info"))


# Тестирование
if __name__ == "__main__":
    assistant = CertificationAssistant()

    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ ПОМОЩНИКА СЕРТИФИКАЦИИ")
    print("=" * 60)

    test_queries = [
        ("пылесос", "", ""),
        ("ноутбук", "ТР ТС 004/2011", ""),
        ("светильник", "", ""),
    ]

    for query, reg, tnved in test_queries:
        print(f"\n🔍 Запрос: '{query}'")
        result = assistant.process_query(query, reg, tnved)

        if result["found"]:
            label, _ = assistant.get_source_label(result["source"])
            print(f"   {label}")
            print(f"   Продукция: {result['product'][:70]}...")
            print(f"   Сертификат: {result['certificate_number']}")
            print(f"   Стандартов: {result['standards_count']}")
        else:
            print(f"   {result['message']}")
