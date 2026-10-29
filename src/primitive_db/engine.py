import shlex

from prettytable import PrettyTable

from primitive_db import core, utils
from primitive_db.constants import META_FILE
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_condition


def print_help() -> None:
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert <имя_таблицы> <значение1> <значение2> .. - добавить запись")
    print("<command> select <имя_таблицы> [where <столбец> = <значение>] - выбрать")
    print("<command> update <имя_таблицы> set <столбец> = <значение> where <условие>")
    print("<command> delete <имя_таблицы> where <столбец> = <значение>")
    print("<command> exit - выход")
    print("<command> help - справка\n")

def run() -> None:
    """Главный цикл программы."""
    print("***База данных***")
    metadata = utils.load_metadata(META_FILE)

    # Создаем кэш для команды select
    cache_select = create_cacher()

    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
            if not user_input:
                continue

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
                utils.save_metadata(META_FILE, metadata)
                cache_select.cache.clear()
                print(f"Таблица '{table_name}' успешно создана.")

            elif command == "drop_table":
                table_name = args[1]
                new_metadata = core.drop_table(metadata, table_name)
                if new_metadata is not None:  # <--- ИЗМЕНЕНИЕ
                    metadata = new_metadata
                    utils.save_metadata(META_FILE, metadata)
                    utils.delete_table_data(table_name)
                    cache_select.cache.clear()
                    print(f"Таблица '{table_name}' успешно удалена.")

            elif command == "insert":
                table_name = args[1]
                if table_name not in metadata:
                    raise ValueError(f"Таблицы '{table_name}' не существует.")
                
                schema = metadata[table_name]
                raw_values = args[2:] 
                
                parsed_vals = []
                for i, val in enumerate(raw_values):
                    col = schema[i + 1] 
                    if col["type"] == "int":
                        parsed_vals.append(int(val))
                    elif col["type"] == "bool":
                        parsed_vals.append(val.lower() in ["true", "1"])
                    else:
                        parsed_vals.append(val)
                
                table_data = utils.load_table_data(table_name)
                table_data = core.insert(table_data, schema, parsed_vals)
                utils.save_table_data(table_name, table_data)
                cache_select.cache.clear()
                print("Запись добавлена.")

            elif command == "select":
                table_name = args[1]
                if table_name not in metadata:
                    raise ValueError(f"Таблицы '{table_name}' не существует.")
                
                where_clause = None
                if "where" in args:
                    idx = args.index("where")
                    where_clause = parse_condition(args[idx+1:], metadata[table_name])
                
                table_data = utils.load_table_data(table_name)
                
                query_key = f"{table_name}_{str(where_clause)}"
                result = cache_select(
                    query_key, lambda: core.select(table_data, where_clause)
                )
                
                if not result:
                    print("Данных нет.")
                else:
                    pt = PrettyTable()
                    pt.field_names = [col["name"] for col in metadata[table_name]]
                    for row in result:
                        pt.add_row(
                            [row.get(col["name"], "") for col in metadata[table_name]]
                        )
                    print(pt)

            elif command == "update":
                table_name = args[1]
                if table_name not in metadata:
                    raise ValueError(f"Таблицы '{table_name}' не существует.")
                
                set_idx = args.index("set")
                where_idx = args.index("where")
                
                set_clause = parse_condition(
                    args[set_idx+1:where_idx], metadata[table_name]
                )
                where_clause = parse_condition(
                    args[where_idx+1:], metadata[table_name]
                )
                
                table_data = utils.load_table_data(table_name)
                table_data = core.update(table_data, set_clause, where_clause)
                utils.save_table_data(table_name, table_data)
                cache_select.cache.clear()
                print("Записи обновлены.")

            elif command == "delete":
                table_name = args[1]
                if table_name not in metadata:
                    raise ValueError(f"Таблицы '{table_name}' не существует.")
                
                where_idx = args.index("where")
                where_clause = parse_condition(
                    args[where_idx+1:], metadata[table_name]
                )
                
                table_data = utils.load_table_data(table_name)
                new_table_data = core.delete(table_data, where_clause)
                
                if new_table_data is not None:  # <--- ИЗМЕНЕНИЕ
                    utils.save_table_data(table_name, new_table_data)
                    cache_select.cache.clear()
                    print("Записи удалены.")

            else:
                print(f"Функции <{command}> нет. Попробуйте снова.")

        except ValueError as e:
            print(f"Неверное значение: {e}. Попробуйте снова.")
        except IndexError:
            print("Неверное значение: недостаточно аргументов. Попробуйте снова.")
        except Exception as e:
            print(f"Ошибка: {e}")
