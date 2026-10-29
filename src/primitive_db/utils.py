import json
import os

from primitive_db.constants import DATA_DIR, META_FILE


def load_metadata(filepath: str = META_FILE) -> dict:
    """Загружает метаданные из JSON. Если файла нет - возвращает пустой словарь."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет метаданные в JSON."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_table_data(table_name: str) -> list:
    """Загружает данные таблицы. Если файла нет - возвращает пустой список."""
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_table_data(table_name: str, data: list) -> None:
    """Сохраняет данные таблицы, создавая папку data при необходимости."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def delete_table_data(table_name: str) -> None:
    """Удаляет файл с данными таблицы (при drop_table)."""
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
