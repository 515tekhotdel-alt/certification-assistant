"""
Отладка парсинга дат и расчёта весовых коэффициентов
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import pandas as pd
from src.database.loader import DataLoader
from src.config import COLUMN_MAPPING

# Загружаем данные
loader = DataLoader()
df = loader.get_dataframe()

date_col = COLUMN_MAPPING["date"]

print("=" * 60)
print("🔍 АНАЛИЗ ДАТ В СЕРТИФИКАТАХ")
print("=" * 60)

# Проверяем первые 10 дат
print(f"\n📅 Первые 10 значений в колонке '{date_col}':")
for i, val in enumerate(df[date_col].head(10)):
    print(f"   {i}: {val} (тип: {type(val).__name__})")

# Пробуем распарсить
print("\n📅 Парсинг дат:")
years = []
for val in df[date_col].head(20):
    try:
        date = pd.to_datetime(val)
        year = date.year
        years.append(year)
        print(f"   {val} → год {year}")
    except Exception as e:
        print(f"   {val} → ОШИБКА: {e}")

# Статистика по годам во всей базе
print("\n📊 Распределение по годам (вся база):")
all_years = []
for val in df[date_col]:
    try:
        date = pd.to_datetime(val)
        all_years.append(date.year)
    except:
        pass

if all_years:
    from collections import Counter

    year_counts = Counter(all_years)
    for year in sorted(year_counts.keys(), reverse=True):
        count = year_counts[year]
        pct = count / len(df) * 100
        print(f"   {year}: {count} сертификатов ({pct:.1f}%)")

# Тест весов
print("\n⚖️ Тест весовых коэффициентов:")


def get_year_weight(date_str, use_weight=True):
    if not use_weight:
        return 1.0
    try:
        date = pd.to_datetime(date_str)
        year = date.year
    except:
        return 0.5

    weights = {2026: 1.0, 2025: 0.8, 2024: 0.6}
    return weights.get(year, 0.4)


for val in df[date_col].head(10):
    weight = get_year_weight(val)
    print(f"   {val} → вес {weight}")