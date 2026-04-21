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
    # Боковая панель
    with st.sidebar:
        st.header("🔍 Фильтры")

        # Выбор технических регламентов
        st.subheader("📜 Технические регламенты")
        reg_004 = st.checkbox("ТР ТС 004/2011", value=False)
        reg_020 = st.checkbox("ТР ТС 020/2011", value=False)

        # Формируем строку фильтра для передачи в process_query
        regulation_filter = ""
        if reg_004 and reg_020:
            regulation_filter = "ТР ТС 004/2011; ТР ТС 020/2011"
        elif reg_004:
            regulation_filter = "ТР ТС 004/2011"
        elif reg_020:
            regulation_filter = "ТР ТС 020/2011"

        st.divider()

        # ТНВЭД
        st.subheader("🔢 ТНВЭД")
        tnved = st.text_input(
            "Первые 4 цифры кода",
            placeholder="Например: 8508",
            max_chars=4,
            help="Оставьте пустым, если не уверены"
        )

        st.divider()

        # Переключатель учёта давности
        st.subheader("⚖️ Учитывать давность")
        use_date_weight = st.toggle("Включить весовые коэффициенты по году", value=False)

        if use_date_weight:
            st.caption("Веса по годам:")
            st.caption("• 2026 → 1.0")
            st.caption("• 2025 → 0.8")
            st.caption("• 2024 → 0.6")
            st.caption("• 2023 и старше → 0.4")

        st.divider()

        # Частотный порог
        st.subheader("📊 Порог рекомендации")
        frequency_threshold = st.slider(
            "Минимальная частота",
            min_value=0.3, max_value=1.0, value=0.5, step=0.05,
            help="Стандарты с частотой выше этого порога считаются рекомендованными"
        )

        st.divider()
        st.caption(f"📊 В базе: {len(assistant.df):,} сертификатов")
    # Основное поле
    # Форма для отправки по Enter
    with st.form(key="search_form"):
        product_query = st.text_input(
            "Введите описание продукции:",
            placeholder="Например: пылесос, ноутбук, светильник, чайник...",
            key="product_input"
        )
        search_clicked = st.form_submit_button("🔍 Анализировать", type="primary")

    if search_clicked and product_query:
        with st.spinner(f"Анализ сертификатов для '{product_query}'..."):
            result = assistant.process_query(
                product_query,
                regulation=regulation_filter,
                tnved=tnved,
                use_date_weight=use_date_weight
            )


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

            # Примеры продукции с чекбоксами
            st.markdown("### 📋 Выберите подходящие модели продукции")
            st.caption("По умолчанию выбраны все. Снимите галочки с неподходящих моделей.")

            # Инициализация состояния чекбоксов (по умолчанию все True)
            if "selected_products" not in st.session_state:
                st.session_state.selected_products = {}

            # Получаем все найденные продукты (не только первые 5)
            all_found_products = result.get("all_products_sample", result["products_sample"])

            selected_indices = []
            for i, product in enumerate(all_found_products):
                # Создаём уникальный ключ для чекбокса
                checkbox_key = f"product_{i}_{product[:30]}"
                # По умолчанию True
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

                checked = st.checkbox(
                    product,
                    value=st.session_state[checkbox_key],
                    key=checkbox_key
                )
                if checked:
                    selected_indices.append(i)

            # Кнопка применения выбора
            apply_selection = st.button("🔄 Пересчитать по выбранным моделям", type="secondary")

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

            # Выбираем колонки в зависимости от режима
            if use_date_weight and "weight_sum" in df_standards.columns:
                df_standards["Вес"] = df_standards["weight_sum"].round(2)
                df_standards = df_standards[["designation", "name", "Вес", "Частота", "Рекомендован"]]
                df_standards.columns = ["Обозначение", "Наименование", "Вес", "Частота", "Рекомендован"]
            else:
                # Считаем count (сколько раз встретился стандарт)
                if "count" not in df_standards.columns and "weight_sum" in df_standards.columns:
                    # Если есть weight_sum, но нет count — используем weight_sum как count (при выключенном весе они равны количеству)
                    df_standards["Кол-во"] = df_standards["weight_sum"].round(0).astype(int)
                else:
                    df_standards["Кол-во"] = df_standards.get("count", 0)
                df_standards = df_standards[["designation", "name", "Кол-во", "Частота", "Рекомендован"]]
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