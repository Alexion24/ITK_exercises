# Реализуйте lru_cache декоратор.
#
# Требования:
# Декоратор должен кешировать результаты вызовов функции на основе её аргументов.
# Если функция вызывается с теми же аргументами, что и ранее, возвращайте результат из кеша вместо повторного выполнения функции.
# Декоратор должно быть возможно использовать двумя способами: с указанием максимального кол-ва элементов и без.

import unittest.mock
from collections import OrderedDict
from functools import wraps


def lru_cache(*dargs, **dkwargs):
    # дефолтный maxsize, если не указан
    default_maxsize = 128

    # вызов без параметров: @lru_cache
    if len(dargs) == 1 and callable(dargs[0]) and not dkwargs:
        func = dargs[0]
        return _lru_cache_decorator(default_maxsize)(func)
    # вызов с параметрами: @lru_cache(maxsize=3)
    return _lru_cache_decorator(dkwargs.get("maxsize", default_maxsize))


def _lru_cache_decorator(maxsize):
    def decorator(func):
        cache = OrderedDict()
        sentinel = object()

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            value = cache.get(key, sentinel)
            if value is not sentinel:
                cache.move_to_end(key)
                return value

            result = func(*args, **kwargs)
            cache[key] = result
            cache.move_to_end(key)

            if maxsize is not None and len(cache) > maxsize:
                cache.popitem(last=False)
            return result

        return wrapper

    return decorator


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

    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 1
    assert decorated(3, 4) == 2
    assert decorated(3, 4) == 2
    assert decorated(5, 6) == 3
    assert decorated(5, 6) == 3
    assert decorated(1, 2) == 4
    assert mocked_func.call_count == 4

    print("Все тесты прошли успешно ✅")
