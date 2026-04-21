"""
Основной сервис классификации — анализ группы сертификатов со статистикой
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
from collections import Counter
from datetime import datetime

from src.database.loader import DataLoader
from src.models.deepseek_client import DeepSeekClient
from src.config import COLUMN_MAPPING


class CertificationAssistant:
    """Помощник эксперта по сертификации с анализом частоты стандартов"""

    def __init__(self):
        self.loader = DataLoader()
        self.df = self.loader.get_dataframe()
        self.deepseek = DeepSeekClient()
        self.all_products = self.loader.get_product_names()

    def _get_year_weight(self, date_str, use_weight: bool = False) -> float:
        """Возвращает весовой коэффициент в зависимости от года сертификата"""
        if not use_weight:
            return 1.0

        try:
            date = pd.to_datetime(date_str)
            year = date.year
        except:
            return 0.5  # если дата не распознана — средний вес

        weights = {
            2026: 1.0,
            2025: 0.8,
            2024: 0.6,
        }
        return weights.get(year, 0.4)  # 2023 и старше → 0.4

    def process_query(self, product_query: str, regulation: str = "", tnved: str = "",
                      use_date_weight: bool = False) -> dict:
        """
        Обрабатывает запрос эксперта.

        Args:
            product_query: описание продукции
            regulation: строка с регламентом (может содержать "ТР ТС 004/2011; ТР ТС 020/2011" или один из них)
            tnved: первые 4 цифры ТНВЭД
            use_date_weight: учитывать ли давность сертификатов
        """
        # Шаг 1: поиск релевантных индексов через DeepSeek
        relevant_indices = self.deepseek.find_relevant_indices(product_query, self.all_products)

        if not relevant_indices:
            return {
                "found": False,
                "source": "none",
                "message": "По вашему запросу ничего не найдено.",
                "certificates_count": 0,
                "total_relevant": 0,
                "standards": [],
                "recommended_standards": [],
                "products_sample": [],
                "regulations": []
            }

        # Шаг 2: получаем строки из DataFrame
        indices = [r["index"] for r in relevant_indices]
        matched_rows = self.df.iloc[indices].copy()
        matched_rows["_match_confidence"] = [r["confidence"] for r in relevant_indices]

        # Шаг 3: фильтрация по регламенту (логическое И для нескольких)
        if regulation:
            # Разбиваем строку фильтра на отдельные регламенты
            required_regs = [r.strip() for r in regulation.split(";") if r.strip()]

            def contains_all_regs(val):
                if pd.isna(val):
                    return False
                val_str = str(val)
                return all(reg in val_str for reg in required_regs)

            matched_rows = matched_rows[matched_rows[COLUMN_MAPPING["regulations"]].apply(contains_all_regs)]

        # Шаг 4: фильтрация по ТНВЭД
        if tnved and len(tnved) >= 4:
            matched_rows = matched_rows[
                matched_rows[COLUMN_MAPPING["tnved"]].fillna("").astype(str).str[:4] == tnved[:4]
                ]

        if matched_rows.empty:
            return {
                "found": False,
                "source": "filtered_out",
                "message": f"Найдено {len(relevant_indices)} похожих сертификатов, но ни один не прошёл фильтры.",
                "certificates_count": 0,
                "total_relevant": len(relevant_indices),
                "standards": [],
                "recommended_standards": [],
                "products_sample": [],
                "regulations": []
            }

        # Шаг 5: анализ стандартов (с учётом или без учёта давности)
        date_col = COLUMN_MAPPING["date"]
        standards_stats = self._analyze_standards_weighted(matched_rows, date_col, use_date_weight)

        # Шаг 6: формирование результата
        return {
            "found": True,
            "source": "group_analysis",
            "query": product_query,
            "certificates_count": len(matched_rows),
            "total_relevant": len(relevant_indices),
            "products_sample": matched_rows[COLUMN_MAPPING["product"]].head(5).tolist(),
            "regulations": self._get_unique_values(matched_rows, "regulations"),
            "standards": standards_stats,
            "recommended_standards": self._get_recommended_standards(standards_stats, threshold=0.5),
            "use_date_weight": use_date_weight
        }

    def _analyze_standards_weighted(self, df: pd.DataFrame, date_col: str, use_weight: bool) -> list:
        """Анализирует частоту стандартов с учётом весов по дате"""
        standards_weights = Counter()  # сумма весов для каждого стандарта
        standards_names = {}
        total_weight = 0.0  # общая сумма весов всех сертификатов

        des_col = COLUMN_MAPPING["standards_designation"]
        name_col = COLUMN_MAPPING["standards_name"]

        for _, row in df.iterrows():
            weight = self._get_year_weight(row[date_col], use_weight)
            total_weight += weight

            des_str = str(row[des_col]) if pd.notna(row[des_col]) else ""
            name_str = str(row[name_col]) if pd.notna(row[name_col]) else ""

            des_list = [d.strip() for d in des_str.split(";") if d.strip()]
            name_list = [n.strip() for n in name_str.split(";") if n.strip()]

            for i, des in enumerate(des_list):
                standards_weights[des] += weight
                if des not in standards_names and i < len(name_list):
                    standards_names[des] = name_list[i]

        # Формируем отсортированный список с частотами
        result = []
        for des, weight_sum in standards_weights.most_common():
            frequency = weight_sum / total_weight if total_weight > 0 else 0
            result.append({
                "designation": des,
                "name": standards_names.get(des, ""),
                "weight_sum": weight_sum,
                "frequency": frequency
            })

        return result

    def _get_recommended_standards(self, standards_stats: list, threshold: float = 0.5) -> list:
        """Возвращает стандарты с частотой выше порога"""
        return [s for s in standards_stats if s["frequency"] >= threshold]

    def _get_unique_values(self, df: pd.DataFrame, col_key: str) -> list:
        """Возвращает уникальные значения из колонки"""
        col = COLUMN_MAPPING[col_key]
        values = set()
        for val in df[col].dropna():
            for v in str(val).split(";"):
                if v.strip():
                    values.add(v.strip())
        return sorted(list(values))

    def get_source_label(self, source: str) -> tuple:
        """Возвращает метку для источника"""
        labels = {
            "group_analysis": ("📊 АНАЛИЗ ГРУППЫ СЕРТИФИКАТОВ", "success"),
            "none": ("❌ НЕ НАЙДЕНО", "error"),
            "filtered_out": ("⚠️ НЕ ПРОШЛИ ФИЛЬТРЫ", "warning")
        }
        return labels.get(source, ("", "info"))