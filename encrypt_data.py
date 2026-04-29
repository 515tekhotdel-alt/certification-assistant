"""
Скрипт для шифрования certificates.xlsx → certificates.enc
Запускается ОДИН РАЗ локально. Ключ сохраняется в .env
"""

from cryptography.fernet import Fernet
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Генерируем или загружаем ключ
key = os.getenv("ENCRYPTION_KEY")
if not key:
    key = Fernet.generate_key().decode()
    print(f"🔑 Новый ключ: {key}")
    print("📝 Сохраните его в .env: ENCRYPTION_KEY=" + key)
else:
    print(f"🔑 Используем ключ из .env")

fernet = Fernet(key.encode())

# Шифруем
input_file = Path("data/certificates.xlsx")
output_file = Path("data/certificates.enc")

with open(input_file, "rb") as f:
    data = f.read()

encrypted = fernet.encrypt(data)

with open(output_file, "wb") as f:
    f.write(encrypted)

print(f"✅ {input_file.name} → {output_file.name}")
print(f"📊 Размер: {len(data):,} → {len(encrypted):,} байт")