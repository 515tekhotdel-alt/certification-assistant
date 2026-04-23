"""
Тест фильтрации на реальных данных
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import pandas as pd
from src.database.loader import DataLoader
from src.config import COLUMN_MAPPING

loader = DataLoader()
df = loader.get_dataframe()

reg_col = COLUMN_MAPPING["regulations"]
product_col = COLUMN_MAPPING["product"]

# Ищем "светильник"
query = "светильник"
matched = df[df[product_col].str.lower().str.contains(query, na=False)]

print(f"Найдено строк со 'светильник': {len(matched)}")
print("-" * 60)

# Показываем первые 10 с регламентами
for i, (_, row) in enumerate(matched.head(10).iterrows()):
    product = str(row[product_col])[:60]
    regs = str(row[reg_col])
    has_004 = "ТР ТС 004/2011" in regs
    has_020 = "ТР ТС 020/2011" in regs
    print(f"{i+1}. {product}")
    print(f"   Регламенты: {regs}")
    print(f"   004: {has_004}, 020: {has_020}")
    print()

# Фильтр "Только 004"
print("=" * 60)
print("ПРИМЕНЯЕМ ФИЛЬТР 'ТОЛЬКО 004'")
print("=" * 60)

filtered = matched[
    matched[reg_col].fillna("").apply(
        lambda x: ("ТР ТС 004/2011" in str(x)) and ("ТР ТС 020/2011" not in str(x))
    )
]

print(f"После фильтра: {len(filtered)} строк")
for _, row in filtered.iterrows():
    print(f"  • {str(row[product_col])[:60]}")
    print(f"    {str(row[reg_col])}")