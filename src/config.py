"""
Конфигурация приложения
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Пути к данным
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CERTIFICATES_FILE = DATA_DIR / "certificates.xlsx"

# API ключи
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = "deepseek-chat"

# Настройки поиска
SIMILARITY_THRESHOLD = 0.85  # Порог для признания точного совпадения

# Колонки в Excel-файле
COLUMN_MAPPING = {
    "date": "Дата регистрации сертификата",
    "number": "Номер",
    "attestation": "Аттестат аккредитации ОС",
    "product": "Полное наименование продукции",
    "regulations": "Технический регламент",
    "tnved": "ТНВЭД",
    "standards_designation": "Обозначение стандарта, нормативного документа",
    "standards_name": "Наименование стандарта, нормативного документа"
}

# Пароль для умного поиска
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")