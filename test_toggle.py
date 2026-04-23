import streamlit as st

st.set_page_config(page_title="Тест доступа", page_icon="🔑")
st.title("🔑 Тест умного поиска")

PASSWORD = "123"

if "ai_enabled" not in st.session_state:
    st.session_state.ai_enabled = False
if "show_password" not in st.session_state:
    st.session_state.show_password = False
if "error_msg" not in st.session_state:
    st.session_state.error_msg = ""

# Кнопка "Включить"
if st.button("🤖 Включить умный поиск", disabled=st.session_state.ai_enabled):
    st.session_state.show_password = True
    st.session_state.error_msg = ""  # ← сбрасываем ошибку
    st.rerun()

# Кнопка "Отключить"
if st.button("🚫 Отключить умный поиск", disabled=not st.session_state.ai_enabled):
    st.session_state.ai_enabled = False
    st.session_state.show_password = False
    st.session_state.error_msg = ""
    st.rerun()

# Поле пароля
if st.session_state.show_password and not st.session_state.ai_enabled:
    pwd = st.text_input("Введите пароль", type="password")

    if st.button("✅ Подтвердить"):
        if pwd == PASSWORD:
            st.session_state.ai_enabled = True
            st.session_state.show_password = False
            st.session_state.error_msg = ""
        else:
            st.session_state.show_password = False
            st.session_state.error_msg = "❌ Неверный пароль"
        st.rerun()

    if st.button("❌ Отмена"):
        st.session_state.show_password = False
        st.rerun()

if st.session_state.error_msg:
    st.error(st.session_state.error_msg)

st.divider()
if st.session_state.ai_enabled:
    st.success("✅ Умный поиск активен")
else:
    st.info("🔒 Умный поиск выключен")