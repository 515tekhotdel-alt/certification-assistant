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
    st.subheader("📜 Технические регламенты")

    # Варианты с красивыми названиями и иконками
    reg_options = ["both", "004_only", "020_only"]
    reg_display = [
        "📋 Оба регламента (ТР ТС 004/2011 + ТР ТС 020/2011)",
        "⚡ Только ТР ТС 004/2011 (без ТР ТС 020/2011)",
        "📡 Только ТР ТС 020/2011 (без ТР ТС 004/2011)"
    ]

    # Инициализация состояния
    if "reg_mode" not in st.session_state:
        st.session_state.reg_mode = "both"

    current_index = reg_options.index(st.session_state.reg_mode)

    selected_index = st.radio(
        "🔍 Выберите вариант фильтрации:",
        options=range(len(reg_options)),
        format_func=lambda i: reg_display[i],
        index=current_index,
        key="regulation_radio"
    )

    selected_mode = reg_options[selected_index]

    if selected_mode != st.session_state.reg_mode:
        st.session_state.reg_mode = selected_mode
        st.rerun()

    return selected_mode