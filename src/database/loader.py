"""
Загрузка и предобработка данных из Excel-файла с сертификатами
"""

import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import CERTIFICATES_FILE, COLUMN_MAPPING


class DataLoader:
    """Класс для загрузки и обработки данных сертификатов"""

    def __init__(self):
        self.df = None
        self.load_data()

    def load_data(self):
        """Загружает данные из Excel-файла"""
        try:
            self.df = pd.read_excel(CERTIFICATES_FILE)
            print(f"✅ Загружено {len(self.df)} строк из {CERTIFICATES_FILE.name}")
        except FileNotFoundError:
            print(f"❌ Файл {CERTIFICATES_FILE} не найден")
            self.df = pd.DataFrame()
        except Exception as e:
            print(f"❌ Ошибка при загрузке файла: {e}")
            self.df = pd.DataFrame()

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