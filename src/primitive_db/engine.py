import shlex

from prettytable import PrettyTable

from primitive_db import core, utils
from primitive_db.constants import META_FILE
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_condition


def print_help() -> None:
    """Выводит справку по командам."""
    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.")  # noqa: E501
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")  # noqa: E501
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")  # noqa: E501
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")  # noqa: E501
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

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
                if new_metadata is not None:
                    metadata = new_metadata
                    utils.save_metadata(META_FILE, metadata)
                    utils.delete_table_data(table_name)
                    cache_select.cache.clear()
                    print(f"Таблица '{table_name}' успешно удалена.")

            elif command == "info":
                table_name = args[1]
                table_data = utils.load_table_data(table_name)
                core.info_table(metadata, table_name, table_data)

            # --- ОБНОВЛЕННЫЕ CRUD КОМАНДЫ ---
            
            elif command == "insert" and len(args) > 1 and args[1] == "into":
                # Синтаксис: insert into users values ("Sergei", 28, true)
                table_name = args[2]
                if table_name not in metadata:
                    raise ValueError(f"Таблицы '{table_name}' не существует.")
                
                schema = metadata[table_name]
                
                # Находим индексы скобок и извлекаем значения
                values_str = " ".join(args[4:]) # Пропускаем insert into users values
                values_str = values_str.strip("()")
                
                # Разделяем по запятой и очищаем от кавычек и пробелов
                raw_values = [v.strip().strip("'\"") for v in values_str.split(",")]
                
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
                print(f"Запись с ID={table_data[-1]['ID']} успешно добавлена в таблицу '{table_name}'.")  # noqa: E501

            elif command == "select" and len(args) > 1 and args[1] == "from":
                # Синтаксис: select from users where age = 28
                table_name = args[2]
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
                # Синтаксис: update users set age = 29 where name = "Sergei"
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
                print(f"Записи в таблице '{table_name}' успешно обновлены.")

            elif command == "delete" and len(args) > 1 and args[1] == "from":
                # Синтаксис: delete from users where ID = 1
                table_name = args[2]
                if table_name not in metadata:
                    raise ValueError(f"Таблицы '{table_name}' не существует.")
                
                where_idx = args.index("where")
                where_clause = parse_condition(
                    args[where_idx+1:], metadata[table_name]
                )
                
                table_data = utils.load_table_data(table_name)
                new_table_data = core.delete(table_data, where_clause)
                
                if new_table_data is not None:
                    utils.save_table_data(table_name, new_table_data)
                    cache_select.cache.clear()
                    print(f"Записи из таблицы '{table_name}' успешно удалены.")

            else:
                print(f"Функции <{command}> нет. Попробуйте снова.")

        except ValueError as e:
            print(f"Некорректное значение: {e}. Попробуйте снова.")
        except IndexError:
            print("Некорректное значение: недостаточно аргументов. Попробуйте снова.")
        except Exception as e:
            print(f"Ошибка: {e}")
