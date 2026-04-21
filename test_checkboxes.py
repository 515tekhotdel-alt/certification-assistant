"""
Тестирование чекбоксов без сброса состояния
"""

import streamlit as st

st.set_page_config(page_title="Тест чекбоксов", page_icon="✅")

st.title("✅ Тест чекбоксов")
st.markdown("Проверяем, что чекбоксы не сбрасываются и не исчезают")

# Тестовый список продуктов
test_products = [
    "Пылесос моющий Karcher SE 4001",
    "Пылесос моющий Thomas TWIN XT",
    "Пылесос бытовой Samsung VC 2400",
    "Пылесос промышленный Cleantech 500",
    "Пылесос робот Xiaomi Vacuum",
]

st.markdown("### Выберите модели:")

# Вариант 1: через session_state явно
if "checkbox_states" not in st.session_state:
    st.session_state.checkbox_states = {f"cb_{i}": True for i in range(len(test_products))}

selected = []
for i, product in enumerate(test_products):
    key = f"cb_{i}"
    checked = st.checkbox(
        product,
        value=st.session_state.checkbox_states[key],
        key=key
    )
    st.session_state.checkbox_states[key] = checked
    if checked:
        selected.append(product)

st.divider()
st.markdown(f"**Выбрано: {len(selected)} из {len(test_products)}**")

if selected:
    st.markdown("**Выбранные модели:**")
    for p in selected:
        st.write(f"- {p}")

# Кнопка для проверки пересчёта
if st.button("🔄 Имитация пересчёта"):
    st.success(f"Пересчёт выполнен для {len(selected)} моделей")