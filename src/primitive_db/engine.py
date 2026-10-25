import shlex
from prettytable import PrettyTable
from primitive_db import core, utils

def print_help() -> None:
    """Выводит справку."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert <имя_таблицы> <значения> - добавить запись")
    print("<command> select <имя_таблицы> [where <условие>] - выбрать записи")
    print("<command> update <имя_таблицы> set <условие> where <условие> - обновить")
    print("<command> delete <имя_таблицы> where <условие> - удалить запись")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def parse_where_args(args: list, schema: list) -> dict:
    """Превращает ['age', '=', '28'] в {'age': 28}"""
    if len(args) != 3 or args[1] != "=":
        raise ValueError("Неверный формат условия. Используйте: <столбец> = <значение>")
    
    col_name, _, val_str = args
    col_type = next((c["type"] for c in schema if c["name"] == col_name), "str")
    
    # Приводим тип
    if col_type == "int":
        val = int(val_str)
    elif col_type == "bool":
        val = val_str.lower() in ["true", "1", "yes"]
    else:
        val = val_str.strip("'\"") # Убираем кавычки для строк
        
    return {col_name: val}

def run() -> None:
    print("***База данных***")
    metadata = utils.load_metadata()

    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
            if not user_input:
                continue

            # Разбиваем строку с учетом кавычек
            args = shlex.split(user_input)
            command = args[0]

            if command == "exit":
                print("Выход...")
                break

            elif command == "help":
                print_help()

            elif command == "list_tables":
                if not metadata:
                    print("Таблиц нет.")
                else:
                    for table in metadata:
                        print(f"- {table}")

            elif command == "create_table":
                table_name = args[1]
                columns = []
                for col_def in args[2:]:
                    name, col_type = col_def.split(":")
                    columns.append({"name": name, "type": col_type})
                
                metadata = core.create_table(metadata, table_name, columns)
                utils.save_metadata(utils.METADATA_FILE, metadata)
                print(f"Таблица '{table_name}' успешно создана со столбцами: " + 
                      ", ".join(f"{c['name']}:{c['type']}" for c in metadata[table_name]))

            elif command == "drop_table":
                table_name = args[1]
                metadata = core.drop_table(metadata, table_name)
                utils.save_metadata(utils.METADATA_FILE, metadata)
                # (Опционально) можно удалить файл данных
                print(f"Таблица '{table_name}' успешно удалена.")

            elif command == "insert":
                table_name = args[1]
                if table_name not in metadata:
                    raise ValueError(f"Таблицы '{table_name}' не существует.")
                
                # Вставляем пустую строку в список (введем значения позже)
                raw_values = " ".join(args[2:])
                
                # В реальной жизни тут нужен сложный парсер, но для простоты 
                # попросим вводить значения через запятую без пробелов: 1,Ivan,25
                vals = raw_values.split(",")
                
                # Пытаемся привести типы
                parsed_vals = []
                for i, val in enumerate(vals):
                    col = metadata[table_name][i+1] # +1, т.к. пропускаем ID
                    val = val.strip("'\" ")
                    if col["type"] == "int": parsed_vals.append(int(val))
                    elif col["type"] == "bool": parsed_vals.append(val.lower() in ["true", "1"])
                    else: parsed_vals.append(val)
                
                table_data = utils.load_table_data(table_name)
                table_data = core.insert(table_data, metadata[table_name], parsed_vals)
                utils.save_table_data(table_name, table_data)
                print("Запись добавлена.")

            elif command == "select":
                table_name = args[1]
                if table_name not in metadata:
                    raise ValueError(f"Таблицы '{table_name}' не существует.")
                
                where_clause = None
                if "where" in args:
                    idx = args.index("where")
                    where_clause = parse_where_args(args[idx+1:], metadata[table_name])
                
                table_data = utils.load_table_data(table_name)
                result = core.select(table_data, where_clause)
                
                # Вывод через PrettyTable
                if not result:
                    print("Данных нет.")
                else:
                    pt = PrettyTable()
                    pt.field_names = [col["name"] for col in metadata[table_name]]
                    for row in result:
                        pt.add_row([row.get(col["name"], "") for col in metadata[table_name]])
                    print(pt)

            elif command == "update":
                table_name = args[1]
                if table_name not in metadata:
                    raise ValueError(f"Таблицы '{table_name}' не существует.")
                
                set_idx = args.index("set")
                where_idx = args.index("where")
                
                set_clause = parse_where_args(args[set_idx+1:where_idx], metadata[table_name])
                where_clause = parse_where_args(args[where_idx+1:], metadata[table_name])
                
                table_data = utils.load_table_data(table_name)
                table_data = core.update(table_data, set_clause, where_clause)
                utils.save_table_data(table_name, table_data)
                print("Записи обновлены.")

            elif command == "delete":
                table_name = args[1]
                if table_name not in metadata:
                    raise ValueError(f"Таблицы '{table_name}' не существует.")
                
                where_idx = args.index("where")
                where_clause = parse_where_args(args[where_idx+1:], metadata[table_name])
                
                table_data = utils.load_table_data(table_name)
                table_data = core.delete(table_data, where_clause)
                utils.save_table_data(table_name, table_data)
                print("Записи удалены.")

            else:
                print(f"Функции <{command}> нет. Попробуйте снова.")

        except ValueError as e:
            print(f"Неверное значение: {e}. Попробуйте снова.")
        except IndexError:
            print("Неверное значение: недостаточно аргументов. Попробуйте снова.")
        except Exception as e:
            print(f"Ошибка: {e}")
