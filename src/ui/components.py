"""
Переиспользуемые UI-компоненты
"""

import streamlit as st


def render_regulation_selector() -> str:
    """
    Отрисовывает radio-кнопки выбора технических регламентов.

    Returns:
        str: режим фильтрации ('both', '004_only', '020_only')
    """
    st.subheader("📑 Технические регламенты")

    # Варианты для отображения и их внутренние значения
    reg_options = ["both", "004_only", "020_only"]
    reg_display = [
        "📋 ТР ТС 004 + ТР ТС 020 + ТР ТС 010",
        "⚡ Только ТР ТС 004 (без ТР ТС 020)",
        "📡 Только ТР ТС 020 (без ТР ТС 004)"
    ]

    # Инициализация индекса по умолчанию (0 = "both")
    if "reg_index" not in st.session_state:
        st.session_state.reg_index = 0

    # Ключ для radio теперь постоянный и привязан к session_state
    selected_index = st.radio(
        " ",
        options=range(len(reg_options)),
        format_func=lambda i: reg_display[i],
        index=st.session_state.reg_index,
        key="##regulation_radio"  # Уникальный ключ, который не меняется
    )

    # Сохраняем выбранный индекс и возвращаем соответствующее значение
    st.session_state.reg_index = selected_index
    return reg_options[selected_index]