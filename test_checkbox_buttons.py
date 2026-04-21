"""
Тестирование чекбоксов с кнопками "Выбрать все" и "Убрать все"
"""

import streamlit as st

st.set_page_config(page_title="Тест чекбоксов", page_icon="✅")

st.title("✅ Тест чекбоксов и кнопок")

products = [
    "Пылесос моющий Karcher SE 4001",
    "Пылесос моющий Thomas TWIN XT",
    "Пылесос бытовой Samsung VC 2400",
    "Пылесос промышленный Cleantech 500",
    "Робот-пылесос Xiaomi Vacuum",
]

query = "test_query"

st.markdown("### Выберите модели:")

# Кнопки
col1, col2 = st.columns(2)
with col1:
    if st.button("✅ Выбрать все", key=f"all_{query}"):
        for i in range(len(products)):
            st.session_state[f"cb_{query}_{i}"] = True
        st.rerun()
with col2:
    if st.button("❌ Убрать все", key=f"none_{query}"):
        for i in range(len(products)):
            st.session_state[f"cb_{query}_{i}"] = False
        st.rerun()

# Чекбоксы
selected = []
for i, p in enumerate(products):
    key = f"cb_{query}_{i}"

    # Явно задаём начальное значение, если ключа нет
    if key not in st.session_state:
        st.session_state[key] = True

    # Важно: используем key, НЕ передаём value
    checked = st.checkbox(p, key=key)

    if checked:
        selected.append(p)

st.divider()
st.markdown(f"**Выбрано: {len(selected)} из {len(products)}**")

# Кнопка пересчёта
if st.button("🔄 Пересчитать", key=f"recalc_{query}"):
    st.success(f"Пересчёт для {len(selected)} моделей")
    for p in selected:
        st.write(f"- {p}")