import json
import os

# Пути к файлам
METADATA_FILE = "db_meta.json"
DATA_DIR = "data"

def load_metadata(filepath: str = METADATA_FILE) -> dict:
    """Загружает метаданные из JSON-файла. Если файла нет, возвращает пустой словарь."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_table_data(table_name: str) -> list:
    """Загружает данные таблицы из папки data/. Если файла нет, возвращает пустой список."""
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_table_data(table_name: str, data: list) -> None:
    """Сохраняет данные таблицы в папку data/."""
    os.makedirs(DATA_DIR, exist_ok=True) # Создаем папку data, если её нет
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
