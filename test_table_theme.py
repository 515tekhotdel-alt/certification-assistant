"""
Тест таблицы через st.markdown — как в Экспертной системе
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Тест таблицы", page_icon="📊", layout="wide")

# Стили — ТОЧНО как в той программе
st.markdown("""
<style>
    .indicator-results-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: auto;
        word-wrap: break-word;
    }
    .indicator-results-table th, .indicator-results-table td {
        border: 1px solid #ddd;
        padding: 6px 8px;
        text-align: left;
        vertical-align: top;
        word-wrap: break-word;
        white-space: normal;
    }
    .indicator-results-table th {
        background-color: #f2f2f2;
        font-weight: 600;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Тест таблицы (как в Экспертной системе)")

data = {
    "Обозначение": ["ГОСТ 123", "ГОСТ 456", "ГОСТ 789"],
    "Наименование": [
        "Электромагнитная совместимость. Требования для бытовых приборов, электрических инструментов и аналогичных устройств. Часть 2. Помехоустойчивость. Стандарт для группы однородной продукции",
        "Безопасность бытовых и аналогичных электрических приборов. Часть 1. Общие требования",
        "Оценка электронного и электрического оборудования в отношении ограничений воздействия на человека электромагнитных полей (0 Гц - 300 ГГц)"
    ],
    "Частота": ["100%", "85%", "67%"],
    "Рекомендован": ["✅", "❓", "✅"]
}

df = pd.DataFrame(data)

# ТОЧНО как в той программе
html_table = df.to_html(index=False, classes='indicator-results-table', escape=False)
st.markdown(html_table, unsafe_allow_html=True)

st.divider()
st.write("Если переключатель тем (три точки) есть — всё работает.")
st.write("Если нет — проблема НЕ в таблице.")
