"""
Удаление дубликатов из certificates.xlsx по номеру сертификата
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import pandas as pd
from src.database.loader import DataLoader
from src.config import COLUMN_MAPPING

loader = DataLoader()
df = loader.get_dataframe()

number_col = COLUMN_MAPPING["number"]

# Показываем статистику ДО
print(f"Всего строк ДО очистки: {len(df)}")
print(f"Уникальных номеров СС: {df[number_col].nunique()}")

# Удаляем дубликаты, оставляя первое вхождение
df_clean = df.drop_duplicates(subset=[number_col], keep="first")

print(f"\nВсего строк ПОСЛЕ очистки: {len(df_clean)}")
print(f"Удалено дубликатов: {len(df) - len(df_clean)}")

# Сохраняем
df_clean.to_excel("data/certificates.xlsx", index=False)
print("\n✅ Файл сохранён. Оригинал перезаписан.")