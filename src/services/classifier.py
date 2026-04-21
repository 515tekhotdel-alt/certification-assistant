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
        self._last_matched_rows = None
        self._last_query = None

    def _get_year_weight(self, date_str, use_weight: bool = False) -> float:
        if not use_weight:
            return 1.0
        try:
            date = pd.to_datetime(date_str)
            year = date.year
        except:
            return 0.5
        weights = {2026: 1.0, 2025: 0.8, 2024: 0.6}
        return weights.get(year, 0.4)

    def process_query(self, product_query: str, regulation: str = "", tnved: str = "",
                      use_date_weight: bool = False) -> dict:
        relevant_indices = self.deepseek.find_relevant_indices(product_query, self.all_products)

        if not relevant_indices:
            return {
                "found": False, "source": "none",
                "message": "По вашему запросу ничего не найдено.",
                "certificates_count": 0, "total_relevant": 0,
                "standards": [], "recommended_standards": [],
                "products_sample": [], "regulations": [],
                "all_products_sample": [], "filtered_products_sample": []
            }

        indices = [r["index"] for r in relevant_indices]
        matched_rows = self.df.iloc[indices].copy()
        matched_rows["_match_confidence"] = [r["confidence"] for r in relevant_indices]
        matched_rows["_original_index"] = indices

        if regulation:
            if regulation == "both":
                def check_both(val):
                    if pd.isna(val): return False
                    val_str = str(val)
                    return ("ТР ТС 004/2011" in val_str) and ("ТР ТС 020/2011" in val_str)

                matched_rows = matched_rows[matched_rows[COLUMN_MAPPING["regulations"]].apply(check_both)]
            elif regulation == "004_only":
                def check_004_only(val):
                    if pd.isna(val): return False
                    val_str = str(val)
                    return ("ТР ТС 004/2011" in val_str) and ("ТР ТС 020/2011" not in val_str)

                matched_rows = matched_rows[matched_rows[COLUMN_MAPPING["regulations"]].apply(check_004_only)]
            elif regulation == "020_only":
                def check_020_only(val):
                    if pd.isna(val): return False
                    val_str = str(val)
                    return ("ТР ТС 020/2011" in val_str) and ("ТР ТС 004/2011" not in val_str)

                matched_rows = matched_rows[matched_rows[COLUMN_MAPPING["regulations"]].apply(check_020_only)]

        if tnved and len(tnved) >= 4:
            matched_rows = matched_rows[
                matched_rows[COLUMN_MAPPING["tnved"]].fillna("").astype(str).str[:4] == tnved[:4]
                ]

        all_products_sample = [r["product"] for r in relevant_indices]

        if matched_rows.empty:
            return {
                "found": False, "source": "filtered_out",
                "message": f"Найдено {len(relevant_indices)} похожих сертификатов, но ни один не прошёл фильтры.",
                "certificates_count": 0, "total_relevant": len(relevant_indices),
                "standards": [], "recommended_standards": [],
                "products_sample": [], "regulations": [],
                "all_products_sample": all_products_sample,
                "filtered_products_sample": []
            }

        self._last_matched_rows = matched_rows.reset_index(drop=True)
        self._last_query = product_query

        date_col = COLUMN_MAPPING["date"]
        standards_stats = self._analyze_standards_weighted(matched_rows, date_col, use_date_weight)

        return {
            "found": True, "source": "group_analysis", "query": product_query,
            "certificates_count": len(matched_rows), "total_relevant": len(relevant_indices),
            "products_sample": matched_rows[COLUMN_MAPPING["product"]].head(5).tolist(),
            "all_products_sample": all_products_sample,
            "filtered_products_sample": matched_rows[COLUMN_MAPPING["product"]].tolist(),
            "regulations": self._get_unique_values(matched_rows, "regulations"),
            "standards": standards_stats,
            "recommended_standards": self._get_recommended_standards(standards_stats, threshold=0.5),
            "use_date_weight": use_date_weight
        }

    def recalculate_with_selected(self, selected_products: list, use_date_weight: bool = False) -> dict:
        """
        Пересчитывает стандарты только по выбранным продуктам (по названиям).
        """
        if self._last_matched_rows is None:
            return None

        # Фильтруем по названиям продуктов
        product_col = COLUMN_MAPPING["product"]
        filtered_rows = self._last_matched_rows[
            self._last_matched_rows[product_col].isin(selected_products)
        ]

        if filtered_rows.empty:
            return None

        date_col = COLUMN_MAPPING["date"]
        standards_stats = self._analyze_standards_weighted(filtered_rows, date_col, use_date_weight)

        return {
            "found": True, "source": "group_analysis_filtered", "query": self._last_query,
            "certificates_count": len(filtered_rows), "total_relevant": len(self._last_matched_rows),
            "products_sample": filtered_rows[product_col].head(5).tolist(),
            "all_products_sample": self._last_matched_rows[product_col].tolist(),
            "filtered_products_sample": filtered_rows[product_col].tolist(),
            "regulations": self._get_unique_values(filtered_rows, "regulations"),
            "standards": standards_stats,
            "recommended_standards": self._get_recommended_standards(standards_stats, threshold=0.5),
            "use_date_weight": use_date_weight
        }

    def _analyze_standards_weighted(self, df: pd.DataFrame, date_col: str, use_weight: bool) -> list:
        standards_weights = Counter()
        standards_names = {}
        total_weight = 0.0

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

        result = []
        for des, weight_sum in standards_weights.most_common():
            frequency = weight_sum / total_weight if total_weight > 0 else 0
            result.append({
                "designation": des,
                "name": standards_names.get(des, ""),
                "weight_sum": weight_sum,
                "frequency": frequency,
                "count": int(weight_sum) if not use_weight else 0
            })
        return result

    def _get_recommended_standards(self, standards_stats: list, threshold: float = 0.5) -> list:
        return [s for s in standards_stats if s["frequency"] >= threshold]

    def _get_unique_values(self, df: pd.DataFrame, col_key: str) -> list:
        col = COLUMN_MAPPING[col_key]
        values = set()
        for val in df[col].dropna():
            for v in str(val).split(";"):
                if v.strip():
                    values.add(v.strip())
        return sorted(list(values))

    def get_source_label(self, source: str) -> tuple:
        labels = {
            "group_analysis": ("📊 АНАЛИЗ ГРУППЫ СЕРТИФИКАТОВ", "success"),
            "group_analysis_filtered": ("📊 АНАЛИЗ ВЫБРАННЫХ МОДЕЛЕЙ", "success"),
            "none": ("❌ НЕ НАЙДЕНО", "error"),
            "filtered_out": ("⚠️ НЕ ПРОШЛИ ФИЛЬТРЫ", "warning")
        }
        return labels.get(source, ("", "info"))