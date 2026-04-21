"""
Переиспользуемые UI-компоненты
"""

import streamlit as st
from src.ui.styles import get_reg_button_styles


def render_regulation_selector() -> str:
    """
    Отрисовывает красивые кнопки выбора технических регламентов.

    Returns:
        str: режим фильтрации ('both', '004_only', '020_only')
    """
    # Применяем стили
    st.markdown(get_reg_button_styles(), unsafe_allow_html=True)

    st.subheader("📜 Технические регламенты")

    # Инициализация состояния
    if "reg_mode" not in st.session_state:
        st.session_state.reg_mode = "both"

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📋 ОБА\n004 + 020",
                     key="reg_both",
                     use_container_width=True,
                     type="primary" if st.session_state.reg_mode == "both" else "secondary"):
            st.session_state.reg_mode = "both"
            st.rerun()

    with col2:
        if st.button("⚡ ТОЛЬКО 004\n(без 020)",
                     key="reg_004",
                     use_container_width=True,
                     type="primary" if st.session_state.reg_mode == "only_004" else "secondary"):
            st.session_state.reg_mode = "only_004"
            st.rerun()

    with col3:
        if st.button("📡 ТОЛЬКО 020\n(без 004)",
                     key="reg_020",
                     use_container_width=True,
                     type="primary" if st.session_state.reg_mode == "only_020" else "secondary"):
            st.session_state.reg_mode = "only_020"
            st.rerun()

    return st.session_state.reg_mode