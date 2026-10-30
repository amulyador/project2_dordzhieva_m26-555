from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time


@handle_db_errors
def validate_type(value, expected_type: str) -> bool:
    """Проверяет соответствие значения типу."""
    if expected_type == "int":
        return isinstance(value, int)
    elif expected_type == "str":
        return isinstance(value, str)
    elif expected_type == "bool":
        return isinstance(value, bool)
    return False

@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list) -> dict:
    """Создает таблицу, добавляя ID в начало."""
    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует.")
    for col in columns:
        if col["type"] not in VALID_TYPES:
            raise ValueError(f"Неподдерживаемый тип данных: {col['type']}")

    if not any(col["name"] == "ID" for col in columns):
        columns.insert(0, {"name": "ID", "type": "int"})
    
    metadata[table_name] = columns
    return metadata

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует.")
    del metadata[table_name]
    return metadata

@handle_db_errors
@log_time
def insert(table_data: list, table_schema: list, values: list) -> list:
    """Вставляет новую запись, генерируя ID."""
    if len(values) != len(table_schema) - 1:
        raise ValueError(f"Ожидалось {len(table_schema) - 1} значений, получено {len(values)}.")  # noqa: E501

    new_id = max([row["ID"] for row in table_data], default=0) + 1
    new_record = {"ID": new_id}
    
    for i, col in enumerate(table_schema[1:]): 
        val = values[i]
        if not validate_type(val, col["type"]):
            raise ValueError(f"Неверный тип для столбца '{col['name']}'. Ожидался {col['type']}.")  # noqa: E501
        new_record[col["name"]] = val
        
    table_data.append(new_record)
    return table_data

@handle_db_errors
@log_time
def select(table_data: list, where_clause: dict = None) -> list:
    """Фильтрует данные по условию."""
    if not where_clause:
        return table_data
    
    result = []
    for row in table_data:
        match = all(row.get(key) == val for key, val in where_clause.items())
        if match:
            result.append(row)
    return result

@handle_db_errors
def update(table_data: list, set_clause: dict, where_clause: dict) -> list:
    """Обновляет записи по условию."""
    for row in table_data:
        match = all(row.get(key) == val for key, val in where_clause.items())
        if match:
            for key, val in set_clause.items():
                if key in row:
                    row[key] = val
    return table_data

@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data: list, where_clause: dict) -> list:
    """Удаляет записи по условию."""
    result = []
    for row in table_data:
        match = all(row.get(key) == val for key, val in where_clause.items())
        if not match:
            result.append(row)
    return result
