"""
CSS стили для приложения
"""

import streamlit as st


def apply_styles():
    """Применяет все стили к приложению"""
    st.markdown("""
    <style>
        /* Общие стили для radio */
        div[data-testid="stRadio"] label {
            padding: 12px 16px !important;
            border-radius: 14px !important;
            margin-bottom: 10px !important;
            transition: all 0.3s ease !important;
            font-weight: 500 !important;
            font-size: 15px !important;
        }

        /* ВЫБОР РЕГЛАМЕНТОВ — градиенты */
        /* Оба регламента — насыщенный фиолетовый */
        div[role="radiogroup"] label:has(input[value="0"]:checked) {
            background: linear-gradient(135deg, #b8a9d4 0%, #9b8ec4 100%) !important;
            color: #1a1a1a !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        }

        /* Только 004 — розовый */
        div[role="radiogroup"] label:has(input[value="1"]:checked) {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(240, 147, 251, 0.4) !important;
        }

        /* Только 020 — голубой */
        div[role="radiogroup"] label:has(input[value="2"]:checked) {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4) !important;
        }

        /* При наведении */
        div[data-testid="stRadio"] label:hover {
            background: rgba(102, 126, 234, 0.08) !important;
        }

        /* Компактные заголовки */
        h1, h2, h3, h4 {
            margin: 10px 0px 5px 0px !important;
        }

        hr {
            margin: 8px 0px !important;
        }

        /* Скрываем меню справа сверху */
        [data-testid="stMainMenu"] {
            display: none !important;
        }
        
                /* Таблица стандартов */
        .indicator-results-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        .indicator-results-table th, .indicator-results-table td {
            border: 1px solid rgba(128, 128, 128, 0.3);
            padding: 8px;
            text-align: left;
            vertical-align: top;
            white-space: normal;
            word-wrap: break-word;
        }
        .indicator-results-table th {
            background-color: rgba(128, 128, 128, 0.15);
            font-weight: 600;
        }
        
    </style>
    """, unsafe_allow_html=True)