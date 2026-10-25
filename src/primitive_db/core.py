def validate_type(value, expected_type: str) -> bool:
    """Проверяет, соответствует ли значение ожидаемому типу."""
    if expected_type == "int":
        return isinstance(value, int)
    elif expected_type == "str":
        return isinstance(value, str)
    elif expected_type == "bool":
        return isinstance(value, bool)
    return False

def create_table(metadata: dict, table_name: str, columns: list) -> dict:
    """Создает таблицу. Добавляет ID, если его нет, и проверяет типы."""
    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует.")

    # Проверяем поддерживаемые типы
    for col in columns:
        if col["type"] not in ["int", "str", "bool"]:
            raise ValueError(f"Неподдерживаемый тип данных: {col['type']}")

    # Автоматически добавляем ID в начало, если его нет
    if not any(col["name"] == "ID" for col in columns):
        columns.insert(0, {"name": "ID", "type": "int"})
    
    metadata[table_name] = columns
    return metadata

def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует.")
    del metadata[table_name]
    return metadata

def insert(table_data: list, table_schema: list, values: list) -> list:
    """Вставляет новую запись. Генерирует ID автоматически."""
    # Проверяем количество значений (без учета ID)
    if len(values) != len(table_schema) - 1:
        raise ValueError(f"Ожидалось {len(table_schema) - 1} значений, получено {len(values)}.")

    # Генерируем новый ID
    new_id = max([row["ID"] for row in table_data], default=0) + 1
    
    new_record = {"ID": new_id}
    
    # Проверяем типы и добавляем в запись (пропускаем ID)
    for i, col in enumerate(table_schema[1:]): 
        val = values[i]
        if not validate_type(val, col["type"]):
            raise ValueError(f"Неверный тип для столбца '{col['name']}'. Ожидался {col['type']}.")
        new_record[col["name"]] = val
        
    table_data.append(new_record)
    return table_data

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

def update(table_data: list, set_clause: dict, where_clause: dict) -> list:
    """Обновляет записи, подходящие под условие."""
    for row in table_data:
        match = all(row.get(key) == val for key, val in where_clause.items())
        if match:
            for key, val in set_clause.items():
                if key in row:
                    row[key] = val
    return table_data

def delete(table_data: list, where_clause: dict) -> list:
    """Удаляет записи, подходящие под условие."""
    result = []
    for row in table_data:
        match = all(row.get(key) == val for key, val in where_clause.items())
        if not match:
            result.append(row) # Оставляем те, что не подошли под условие
    return result
