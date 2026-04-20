"""
Помощник эксперта по сертификации
Приложение для подбора стандартов на основе базы выданных сертификатов
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd

from src.services.classifier import CertificationAssistant


# Настройка страницы
st.set_page_config(
    page_title="Помощник эксперта по сертификации",
    page_icon="📋",
    layout="wide"
)

@st.cache_resource
def get_assistant():
    return CertificationAssistant()


def main():
    st.title("📋 Помощник эксперта по сертификации")
    st.markdown("### Подбор стандартов на основе анализа группы сертификатов")
    st.caption("Система находит все похожие сертификаты и рассчитывает частоту применения каждого стандарта")

    with st.spinner("Загрузка базы сертификатов..."):
        assistant = get_assistant()

    # Боковая панель
    with st.sidebar:
        st.header("🔍 Фильтры")

        regulation = st.text_input(
            "Технический регламент",
            placeholder="Например: ТР ТС 004/2011",
            help="Оставьте пустым, если не уверены"
        )

        tnved = st.text_input(
            "ТНВЭД (4 цифры)",
            placeholder="Например: 8508",
            max_chars=4,
            help="Первые 4 цифры кода ТНВЭД"
        )

        st.divider()
        st.caption(f"📊 В базе: {len(assistant.df):,} сертификатов")

        # Частотный порог
        st.divider()
        frequency_threshold = st.slider(
            "Порог частоты для рекомендации",
            min_value=0.3, max_value=1.0, value=0.5, step=0.05,
            help="Стандарты с частотой выше этого порога считаются рекомендованными"
        )

    # Основное поле
    product_query = st.text_input(
        "Введите описание продукции:",
        placeholder="Например: пылесос, ноутбук, светильник, чайник...",
        key="product_input"
    )

    search_clicked = st.button("🔍 Анализировать", type="primary", disabled=not product_query)

    if search_clicked and product_query:
        with st.spinner(f"Анализ сертификатов для '{product_query}'..."):
            result = assistant.process_query(product_query, regulation, tnved)

        if result["found"]:
            label, label_type = assistant.get_source_label(result["source"])

            if label_type == "success":
                st.success(label)
            else:
                st.info(label)

            # Метрики
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📦 Найдено сертификатов", result["certificates_count"])
            with col2:
                st.metric("📚 Всего уникальных стандартов", len(result["standards"]))
            with col3:
                recommended = [s for s in result["standards"] if s["frequency"] >= frequency_threshold]
                st.metric("✅ Рекомендовано стандартов", len(recommended))

            # Примеры продукции
            with st.expander("📋 Примеры найденной продукции", expanded=False):
                for p in result["products_sample"]:
                    st.write(f"• {p}")

            # Технические регламенты
            if result["regulations"]:
                st.markdown("**📜 Технические регламенты (в найденных сертификатах):**")
                st.write(", ".join(result["regulations"]))

            st.markdown("---")

            # Таблица стандартов с частотами
            st.markdown("### 📊 Стандарты и частота их применения")

            df_standards = pd.DataFrame(result["standards"])
            df_standards["Частота"] = df_standards["frequency"].apply(lambda x: f"{x:.1%}")
            df_standards["Рекомендован"] = df_standards["frequency"] >= frequency_threshold
            df_standards = df_standards[["designation", "name", "count", "Частота", "Рекомендован"]]
            df_standards.columns = ["Обозначение", "Наименование", "Кол-во", "Частота", "Рекомендован"]

            st.dataframe(
                df_standards,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Обозначение": st.column_config.TextColumn(width="medium"),
                    "Наименование": st.column_config.TextColumn(width="large"),
                    "Кол-во": st.column_config.NumberColumn(width="small"),
                    "Частота": st.column_config.TextColumn(width="small"),
                    "Рекомендован": st.column_config.CheckboxColumn(width="small"),
                }
            )

            # Итоговый список рекомендованных
            st.markdown("---")
            st.markdown(f"### ✅ Рекомендованные стандарты (частота ≥ {frequency_threshold:.0%})")

            if recommended:
                for s in recommended:
                    st.markdown(f"- **{s['designation']}** — {s['name']} *(встречается в {s['frequency']:.1%} сертификатов)*")
            else:
                st.info(f"Нет стандартов с частотой ≥ {frequency_threshold:.0%}")

        else:
            st.error(result["message"])
            if result.get("certificates_count", 0) > 0:
                st.info(f"💡 Всего найдено похожих сертификатов: {result['certificates_count']}, но они отфильтрованы. Попробуйте убрать фильтры.")

    elif search_clicked and not product_query:
        st.warning("Введите описание продукции")


if __name__ == "__main__":
    main()