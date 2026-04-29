"""
Загрузка и предобработка данных из Excel-файла с сертификатами
Поддерживает как обычный .xlsx, так и зашифрованный .enc
"""

import pandas as pd
from pathlib import Path
import sys
import os
from io import BytesIO

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import CERTIFICATES_FILE, COLUMN_MAPPING, ENCRYPTION_ENABLED


class DataLoader:
    """Класс для загрузки и обработки данных сертификатов"""

    def __init__(self):
        self.df = None
        self.load_data()

    def load_data(self):
        """Загружает данные из Excel-файла (обычного или зашифрованного)"""
        try:
            if ENCRYPTION_ENABLED and str(CERTIFICATES_FILE).endswith('.enc'):
                self._load_encrypted()
            else:
                self._load_plain()
        except FileNotFoundError:
            print(f"❌ Файл {CERTIFICATES_FILE} не найден")
            self.df = pd.DataFrame()
        except Exception as e:
            print(f"❌ Ошибка при загрузке файла: {e}")
            self.df = pd.DataFrame()

    def _load_plain(self):
        """Загружает обычный Excel-файл"""
        self.df = pd.read_excel(CERTIFICATES_FILE)
        print(f"✅ Загружено {len(self.df)} строк из {CERTIFICATES_FILE.name}")

    def _load_encrypted(self):
        """Расшифровывает и загружает зашифрованный файл"""
        from cryptography.fernet import Fernet

        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY не найден в переменных окружения")

        fernet = Fernet(key.encode())

        with open(CERTIFICATES_FILE, "rb") as f:
            encrypted_data = f.read()

        decrypted_data = fernet.decrypt(encrypted_data)

        self.df = pd.read_excel(BytesIO(decrypted_data))
        print(f"✅ Расшифровано и загружено {len(self.df)} строк из {CERTIFICATES_FILE.name}")

    def get_dataframe(self) -> pd.DataFrame:
        """Возвращает загруженный DataFrame"""
        return self.df

    def get_product_names(self) -> list:
        """Возвращает список всех наименований продукции"""
        if self.df is not None and not self.df.empty:
            return self.df[COLUMN_MAPPING["product"]].tolist()
        return []


# Для тестирования модуля
if __name__ == "__main__":
    loader = DataLoader()
    df = loader.get_dataframe()
    if not df.empty:
        print(f"\nКолонки в файле:")
        for col in df.columns:
            print(f"  - {col}")
        print(f"\nПервые 3 строки:")
        print(df.head(3))