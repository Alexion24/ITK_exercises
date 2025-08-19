import collections
import functools
import unittest.mock


def lru_cache(func=None, *, maxsize=None):
    """Декоратор LRU cache.
    Поддерживает использование как @lru_cache так и @lru_cache(maxsize=N).
    """

    def decorator(f):
        cache = collections.OrderedDict()

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Создаем ключ на основе аргументов
            key = (args, frozenset(kwargs.items()))
            if key in cache:
                cache.move_to_end(key)  # Использовался недавно
                return cache[key]

            result = f(*args, **kwargs)
            cache[key] = result
            cache.move_to_end(key)

            if maxsize is not None and len(cache) > maxsize:
                cache.popitem(last=False)  # Удаляем самый старый элемент

            return result

        return wrapper

    if func is None:
        # вызвано как @lru_cache(maxsize=...)
        return decorator
    else:
        # вызвано как @lru_cache
        return decorator(func)


@lru_cache
def sum(a: int, b: int) -> int:
    return a + b


@lru_cache
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@lru_cache(maxsize=3)
def multiply(a: int, b: int) -> int:
    return a * b


if __name__ == "__main__":
    assert sum(1, 2) == 3
    assert sum(3, 4) == 7

    assert multiply(1, 2) == 2
    assert multiply(3, 4) == 12

    assert sum_many(1, 2, c=3, d=4) == 10

    mocked_func = unittest.mock.Mock()
    mocked_func.side_effect = [1, 2, 3, 4]

    decorated = lru_cache(maxsize=2)(mocked_func)
    assert decorated(1, 2) == 1  # вызов функции
    assert decorated(1, 2) == 1  # из кеша
    assert decorated(3, 4) == 2  # вызов функции
    assert decorated(3, 4) == 2  # из кеша
    assert decorated(5, 6) == 3  # вызов функции, вытеснит (1,2)
    assert decorated(5, 6) == 3  # из кеша
    assert decorated(1, 2) == 4  # повторный вызов, так как было вытеснено
    assert mocked_func.call_count == 4

    print("Все тесты пройдены ✅")
