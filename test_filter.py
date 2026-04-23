"""
Тест фильтрации по регламентам
"""

import pandas as pd

# Тестовые данные
data = [
    {"product": "Светильник-ночник аккумуляторный", "regulations": "ТР ТС 020/2011"},
    {"product": "Светильник светодиодный", "regulations": "ТР ТС 020/2011; ТР ЕАЭС 037/2016; ТР ТС 004/2011"},
    {"product": "Светильник стационарный", "regulations": "ТР ТС 020/2011; ТР ТС 004/2011"},
    {"product": "Прожектор светодиодный", "regulations": "ТР ТС 020/2011; ТР ТС 004/2011"},
    {"product": "Лампа настольная", "regulations": "ТР ТС 004/2011"},
]

df = pd.DataFrame(data)

print("=" * 60)
print("ТЕСТ ФИЛЬТРАЦИИ ПО РЕГЛАМЕНТАМ")
print("=" * 60)

# Тест "Только 004" (должен быть 004, НЕ должно быть 020)
print("\n📋 Фильтр: ТОЛЬКО 004 (без 020)")
print("Ожидание: только 'Лампа настольная'")
print("-" * 40)

for _, row in df.iterrows():
    val = str(row["regulations"])
    has_004 = "ТР ТС 004/2011" in val
    has_020 = "ТР ТС 020/2011" in val
    passes = has_004 and not has_020
    status = "✅ ПРОХОДИТ" if passes else "❌ НЕ ПРОХОДИТ"
    print(f"  {status}: {row['product']}")
    print(f"    Регламенты: {val}")
    print(f"    004: {has_004}, 020: {has_020}")

# Тест "Только 020" (должен быть 020, НЕ должно быть 004)
print("\n📋 Фильтр: ТОЛЬКО 020 (без 004)")
print("Ожидание: только 'Светильник-ночник аккумуляторный'")
print("-" * 40)

for _, row in df.iterrows():
    val = str(row["regulations"])
    has_004 = "ТР ТС 004/2011" in val
    has_020 = "ТР ТС 020/2011" in val
    passes = has_020 and not has_004
    status = "✅ ПРОХОДИТ" if passes else "❌ НЕ ПРОХОДИТ"
    print(f"  {status}: {row['product']}")
    print(f"    Регламенты: {val}")
    print(f"    004: {has_004}, 020: {has_020}")

# Тест "Оба"
print("\n📋 Фильтр: ОБА (004 И 020)")
print("Ожидание: 'Светильник стационарный', 'Прожектор светодиодный'")
print("-" * 40)

for _, row in df.iterrows():
    val = str(row["regulations"])
    has_004 = "ТР ТС 004/2011" in val
    has_020 = "ТР ТС 020/2011" in val
    passes = has_004 and has_020
    status = "✅ ПРОХОДИТ" if passes else "❌ НЕ ПРОХОДИТ"
    print(f"  {status}: {row['product']}")
    print(f"    Регламенты: {val}")
    print(f"    004: {has_004}, 020: {has_020}")