import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from streamlit_theme import st_theme

st.set_page_config(page_title="Тест таблицы", page_icon="📊", layout="wide")

st.title("📊 Тест таблицы с переносом текста")

# Определяем текущую тему
theme = st_theme()
is_dark = theme.get("base") == "dark" if theme else False

# Цвета для светлой и тёмной темы
if is_dark:
    bg_color = "#0E1117"
    text_color = "#FAFAFA"
    th_bg = "#2e2e2e"
    th_border = "#444"
    td_border = "#333"
else:
    bg_color = "#FFFFFF"
    text_color = "#262730"
    th_bg = "#f0f2f6"
    th_border = "#ddd"
    td_border = "#eee"

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

def dataframe_to_html_with_wrap(df):
    html = df.to_html(index=False, escape=False, border=0, classes="dataframe")
    style = f"""
    <style>
        body {{
            font-family: 'Source Sans Pro', sans-serif;
            margin: 0;
            padding: 0;
            background-color: {bg_color};
        }}
        .dataframe {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            color: {text_color};
        }}
        .dataframe th {{
            background-color: {th_bg};
            font-weight: 600;
            text-align: left;
            padding: 10px 8px;
            border-bottom: 2px solid {th_border};
            color: {text_color};
        }}
        .dataframe td {{
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid {td_border};
            vertical-align: top;
            white-space: normal !important;
            word-wrap: break-word !important;
            word-break: break-word !important;
            color: {text_color};
        }}
        .dataframe td:nth-child(2) {{
            max-width: 600px;
        }}
    </style>
    """
    return style + html

html_table = dataframe_to_html_with_wrap(df)
components.html(html_table, height=400, scrolling=True)