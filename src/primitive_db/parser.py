def parse_condition(args: list, schema: list) -> dict:
    """Превращает ['age', '=', '28'] в {'age': 28}."""
    args = [arg for arg in args if arg.lower() != "and"]
    if len(args) == 0 or len(args) % 3 != 0:
        raise ValueError("Неверный формат условия.")
    conditions = {}
    for i in range(0, len(args), 3):
        col_name, operator, val_str = args[i:i+3]
        if operator != "=":
            raise ValueError("Неверный оператор. Используйте '='")
        col_type = next((c["type"] for c in schema if c["name"] == col_name), "str")
        if col_type == "int":
            val = int(val_str)
        elif col_type == "bool":
            val = val_str.lower() in ["true", "1", "yes"]
        else:
            val = val_str
        conditions[col_name] = val
    return conditions
