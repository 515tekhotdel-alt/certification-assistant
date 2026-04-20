"""
Основной сервис классификации — анализ группы сертификатов со статистикой
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
from collections import Counter

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

    def process_query(self, product_query: str, regulation: str = "", tnved: str = "") -> dict:
        """
        Обрабатывает запрос эксперта.

        Returns:
            dict с результатами анализа группы сертификатов
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

        # Шаг 3: фильтрация по регламенту и ТНВЭД
        if regulation:
            matched_rows = matched_rows[
                matched_rows[COLUMN_MAPPING["regulations"]].fillna("").str.contains(regulation, na=False)
            ]

        if tnved and len(tnved) >= 4:
            matched_rows = matched_rows[
                matched_rows[COLUMN_MAPPING["tnved"]].fillna("").str[:4] == tnved[:4]
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

        # Шаг 4: анализ стандартов
        standards_stats = self._analyze_standards(matched_rows)

        # Шаг 5: формирование результата
        return {
            "found": True,
            "source": "group_analysis",
            "query": product_query,
            "certificates_count": len(matched_rows),
            "total_relevant": len(relevant_indices),
            "products_sample": matched_rows[COLUMN_MAPPING["product"]].head(5).tolist(),
            "regulations": self._get_unique_values(matched_rows, "regulations"),
            "standards": standards_stats,
            "recommended_standards": self._get_recommended_standards(standards_stats, threshold=0.5)
        }

    def _analyze_standards(self, df: pd.DataFrame) -> list:
        """Анализирует частоту стандартов в группе сертификатов"""
        total = len(df)
        standards_counter = Counter()
        standards_names = {}

        des_col = COLUMN_MAPPING["standards_designation"]
        name_col = COLUMN_MAPPING["standards_name"]

        for _, row in df.iterrows():
            des_str = str(row[des_col]) if pd.notna(row[des_col]) else ""
            name_str = str(row[name_col]) if pd.notna(row[name_col]) else ""

            des_list = [d.strip() for d in des_str.split(";") if d.strip()]
            name_list = [n.strip() for n in name_str.split(";") if n.strip()]

            for i, des in enumerate(des_list):
                standards_counter[des] += 1
                if des not in standards_names and i < len(name_list):
                    standards_names[des] = name_list[i]

        # Формируем отсортированный список с частотами
        result = []
        for des, count in standards_counter.most_common():
            result.append({
                "designation": des,
                "name": standards_names.get(des, ""),
                "count": count,
                "frequency": count / total
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