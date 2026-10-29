import functools
import time


def handle_db_errors(func):
    """Перехватывает ошибки БД и выводит их."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, FileNotFoundError) as e:
            print(f"Ошибка базы данных: {e}")
            # Возвращаем первый аргумент, чтобы не сломать программу
            return args[0] if args else None
    return wrapper

def confirm_action(action_name):
    """Запрашивает подтверждение перед опасной операцией."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ans = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ').strip().lower()  # noqa: E501
            if ans == 'y':
                return func(*args, **kwargs)
            else:
                print("Операция отменена.")
                return None  # <--- ИЗМЕНЕНИЕ: возвращаем None при отказе
        return wrapper
    return decorator

def log_time(func):
    """Замеряет время выполнения функции."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f"Функция {func.__name__} выполнялась за {end - start:.3f} секунд")
        return result
    return wrapper

def create_cacher():
    """Замыкание для кэширования результатов."""
    cache = {}
    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result
    
    # Добавляем метод для очистки кэша (пригодится при изменении данных)
    cache_result.cache = cache 
    return cache_result
