"""
CSS-стили для приложения
"""

def get_reg_button_styles() -> str:
    """Возвращает CSS для кнопок выбора регламентов"""
    return """
    <style>
    .reg-btn-both {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .reg-btn-004 {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .reg-btn-020 {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .reg-btn-inactive {
        background: #e0e0e0;
        color: #888;
        font-weight: normal;
        border: none;
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        opacity: 0.6;
    }
    </style>
    """

def get_global_styles() -> str:
    """Возвращает глобальные CSS-стили"""
    return """
    <style>
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 16px;
        padding: 16px;
        margin: 8px 0;
    }
    </style>
    """