"""
Помощник эксперта по сертификации
Приложение для подбора стандартов на основе базы выданных сертификатов
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from io import BytesIO
import os
import streamlit.components.v1 as components

from src.services.classifier import CertificationAssistant
from src.ui.styles import apply_styles

st.set_page_config(
    page_title="Помощник эксперта по сертификации",
    page_icon="📋",
    layout="wide"
)

apply_styles()


@st.cache_resource
def get_assistant():
    return CertificationAssistant()


def main():
    st.title("📋 Помощник эксперта по сертификации")
    st.markdown("### Подбор стандартов на основе анализа группы сертификатов")
    st.caption("Система находит все похожие сертификаты и рассчитывает частоту применения каждого стандарта")

    with st.spinner("Загрузка базы сертификатов..."):
        assistant = get_assistant()

    with st.sidebar:
        from src.ui.components import render_regulation_selector
        reg_mode = render_regulation_selector().strip()
        regulation_filter = reg_mode

        st.divider()

        st.subheader("🔢 ТНВЭД")
        tnved = st.text_input(
            "Первые 4 цифры кода",
            placeholder="Например: 8508",
            max_chars=4,
            help="Оставьте пустым, если не уверены"
        )

        st.divider()

        st.subheader("⚖️ Учитывать давность")
        use_date_weight = st.toggle("Включить весовые коэффициенты по году", value=False)

        if use_date_weight:
            st.caption("Веса по годам:")
            st.caption("• 2026 → 1.0")
            st.caption("• 2025 → 0.8")
            st.caption("• 2024 → 0.6")
            st.caption("• 2023 и старше → 0.4")

        frequency_threshold = 0.5

        st.divider()
        st.subheader("🤖 Умный поиск (DeepSeek)")

        if "ai_enabled" not in st.session_state:
            st.session_state.ai_enabled = False
        if "show_password" not in st.session_state:
            st.session_state.show_password = False
        if "error_msg" not in st.session_state:
            st.session_state.error_msg = ""

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Вкл.", disabled=st.session_state.ai_enabled, use_container_width=True):
                st.session_state.show_password = True
                st.session_state.error_msg = ""
                st.rerun()
        with col2:
            if st.button("🚫 Откл.", disabled=not st.session_state.ai_enabled, use_container_width=True):
                st.session_state.ai_enabled = False
                st.session_state.show_password = False
                st.session_state.error_msg = ""
                st.rerun()

        if st.session_state.show_password and not st.session_state.ai_enabled:
            with st.form(key="password_form"):
                ai_password = st.text_input("Введите пароль", type="password", key="ai_pass_input")
                col_ok, col_cancel = st.columns(2)
                with col_ok:
                    ok_btn = st.form_submit_button("✅ ОК", use_container_width=True)
                with col_cancel:
                    cancel_btn = st.form_submit_button("❌ Отмена", use_container_width=True)

                if ok_btn:
                    if ai_password == os.getenv("ADMIN_PASSWORD", "admin123"):
                        st.session_state.ai_enabled = True
                        st.session_state.show_password = False
                        st.session_state.error_msg = ""
                    else:
                        st.session_state.show_password = False
                        st.session_state.error_msg = "❌ Неверный пароль"
                    st.rerun()

                if cancel_btn:
                    st.session_state.show_password = False
                    st.rerun()

        if st.session_state.error_msg:
            st.error(st.session_state.error_msg)
        if st.session_state.ai_enabled:
            st.success("🤖 Умный поиск активен")

            try:
                balance_data = assistant.deepseek.check_balance()
                if balance_data.get("is_available"):
                    for info in balance_data.get("balance_infos", []):
                        total = info.get("total_balance", "0.00")
                        currency = info.get("currency", "USD")
                        st.caption(f"💰 Баланс: {total} {currency}")
            except:
                pass

        use_ai = st.session_state.ai_enabled

        st.divider()
        st.caption(f"📊 В базе: {len(assistant.df):,} сертификатов")

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
                use_date_weight=use_date_weight,
                use_ai=st.session_state.ai_enabled
            )
            st.session_state.last_result = result
            st.session_state.last_query = product_query

    if "last_result" in st.session_state:
        result = st.session_state.last_result
        product_query = st.session_state.get("last_query", "")

        if result["found"]:
            label, label_type = assistant.get_source_label(result["source"])

            if label_type == "success":
                st.success(label)
            else:
                st.info(label)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📦 Найдено сертификатов", result["certificates_count"])
            with col2:
                st.metric("📚 Всего уникальных стандартов", len(result["standards"]))
            with col3:
                recommended = [s for s in result["standards"] if s["frequency"] >= frequency_threshold]
                st.metric("✅ Рекомендовано стандартов", len(recommended))

            with st.expander("📋 Примеры найденной продукции"):
                for p in result["products_sample"]:
                    st.write(f"• {p}")

            st.markdown("---")

            all_found_products = result.get("filtered_products_sample", result.get("all_products_sample", []))

            with st.expander(f"📋 Выберите подходящие модели продукции ({len(all_found_products)} шт.)", expanded=False):
                st.caption("По умолчанию выбраны все. Снимите галочки с неподходящих моделей.")

                col_all, col_none = st.columns(2)
                with col_all:
                    if st.button("✅ Выбрать все", key=f"select_all_{product_query}", use_container_width=True):
                        for i in range(len(all_found_products)):
                            st.session_state[f"product_cb_{product_query}_{i}"] = True
                        st.rerun()
                with col_none:
                    if st.button("❌ Убрать все", key=f"select_none_{product_query}", use_container_width=True):
                        for i in range(len(all_found_products)):
                            st.session_state[f"product_cb_{product_query}_{i}"] = False
                        st.rerun()

                with st.container():
                    selected_products = []
                    for i, product in enumerate(all_found_products):
                        key = f"product_cb_{product_query}_{i}"

                        if key not in st.session_state:
                            st.session_state[key] = True

                        checked = st.checkbox(product, key=key)

                        if checked:
                            selected_products.append(product)

                st.caption(f"Выбрано: {len(selected_products)} из {len(all_found_products)}")

                if st.button("🔄 Пересчитать стандарты по выбранным моделям",
                             key=f"recalc_{product_query}",
                             type="secondary"):
                    if selected_products:
                        new_result = assistant.recalculate_with_selected(
                            selected_products,
                            use_date_weight=use_date_weight
                        )
                        if new_result:
                            st.session_state.last_result = new_result
                            st.rerun()
                        else:
                            st.warning("Не удалось пересчитать. Попробуйте снова.")
                    else:
                        st.warning("Выберите хотя бы одну модель.")

            st.markdown("---")
            st.markdown("### 📊 Стандарты и частота их применения")

            df_standards = pd.DataFrame(result["standards"])
            df_standards["Частота"] = df_standards["frequency"].apply(lambda x: f"{x:.1%}")
            df_standards["Рекомендован"] = df_standards["frequency"] >= frequency_threshold
            df_standards["Рекомендован"] = df_standards["Рекомендован"].map({True: "✅", False: "❓"})

            if use_date_weight and "weight_sum" in df_standards.columns:
                df_standards["Вес"] = df_standards["weight_sum"].round(2)
                df_standards = df_standards[["designation", "name", "Вес", "Частота", "Рекомендован"]]
                df_standards.columns = ["Обозначение", "Наименование", "Вес", "Частота", "Рекомендован"]
            else:
                if "count" not in df_standards.columns and "weight_sum" in df_standards.columns:
                    df_standards["Кол-во"] = df_standards["weight_sum"].round(0).astype(int)
                else:
                    df_standards["Кол-во"] = df_standards.get("count", 0)
                df_standards = df_standards[["designation", "name", "Кол-во", "Частота", "Рекомендован"]]
                df_standards.columns = ["Обозначение", "Наименование", "Кол-во", "Частота", "Рекомендован"]

            def dataframe_to_html_with_wrap(df):
                html = df.to_html(index=False, escape=False, border=0, classes="dataframe")
                style = f"""
                <style>
                    body {{
                        font-family: 'Source Sans Pro', sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #FFFFFF;
                    }}
                    .dataframe {{
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 14px;
                        color: #262730;
                    }}
                    .dataframe th {{
                        background-color: #f0f2f6;
                        font-weight: 600;
                        text-align: left;
                        padding: 10px 8px;
                        border-bottom: 2px solid #ddd;
                        color: #262730;
                    }}
                    .dataframe td {{
                        text-align: left;
                        padding: 8px;
                        border-bottom: 1px solid #eee;
                        vertical-align: top;
                        white-space: normal !important;
                        word-wrap: break-word !important;
                        word-break: break-word !important;
                        color: #262730;
                    }}
                    .dataframe td:nth-child(2) {{
                        max-width: 600px;
                    }}
                    .dataframe td:nth-child(3) {{
                        min-width: 80px;
                    }}
                </style>
                """
                return style + html

            html_table = dataframe_to_html_with_wrap(df_standards)
            components.html(html_table, height=35 * (len(df_standards) + 2), scrolling=True)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_standards.to_excel(writer, index=False, sheet_name='Стандарты')

                worksheet = writer.sheets['Стандарты']

                from openpyxl.styles import Alignment

                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        cell.alignment = Alignment(wrap_text=True, vertical='top')
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 60)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            st.download_button(
                label="📥 Скачать таблицу (Excel)",
                data=output.getvalue(),
                file_name=f"standards_{product_query.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.markdown("---")
            st.markdown(f"### ✅ Рекомендованные стандарты (частота ≥ {frequency_threshold:.0%})")

            if recommended:
                for s in recommended:
                    st.markdown(
                        f"- **{s['designation']}** — {s['name']} *(встречается в {s['frequency']:.1%} сертификатов)*")
            else:
                st.info(f"Нет стандартов с частотой ≥ {frequency_threshold:.0%}")

        else:
            st.error(result["message"])
            if result.get("certificates_count", 0) > 0:
                st.info(
                    f"💡 Всего найдено похожих сертификатов: {result['certificates_count']}, но они отфильтрованы. Попробуйте убрать фильтры.")

    elif search_clicked and not product_query:
        st.warning("Введите описание продукции")


if __name__ == "__main__":
    main()