# Задача - Распределенный лок
# У вас есть распределенное приложение работающее на десятках серверах.
# Вам необходимо написать декоратор single который гарантирует, что декорируемая функция не исполняется параллельно.

import datetime
import functools
import multiprocessing
import time
import uuid

import redis

# Подключение к Redis вне функции (один раз)
r = redis.StrictRedis.from_url("redis://localhost:6379/0")

# Скрипты на Lua в Redis выполняются атомарно, что гарантирует отсутствие гонок в проверке и удалении
RELEASE_LUA = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""


class SingleExecutionError(Exception):
    """Функция уже выполняется в другом процессе/узле"""

    pass


def single(max_processing_time: datetime.timedelta):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_key = f"single:{func.__module__}.{func.__qualname__}"
            lock_id = str(uuid.uuid4())
            ttl = int(max_processing_time.total_seconds())
            acquired = r.set(lock_key, lock_id, nx=True, ex=ttl)
            if not acquired:
                raise SingleExecutionError()
            try:
                return func(*args, **kwargs)
            finally:
                r.eval(RELEASE_LUA, 1, lock_key, lock_id)

        return wrapper

    return decorator


# Параметр max_processing_time указывает на максимально допустимое время работы декорируемой функции.
@single(max_processing_time=datetime.timedelta(minutes=2))
def process_transaction(instance_id: int):
    print(f"[{instance_id}] - Start processing")
    time.sleep(2)
    print(f"[{instance_id}] - End processing")


def worker(instance_id: int):
    try:
        process_transaction(instance_id)
    except SingleExecutionError:
        print(f"[{instance_id}] - Locked, skipping execution")

if __name__ == "__main__":
    # Запускаем несколько процессов параллельно, чтобы проверить блокировку
    process_count = 5
    with multiprocessing.Pool(process_count) as pool:
        pool.map(worker, range(process_count))


# запускаем redis в докере (если он не запущен)
# docker run -d --name redis -p 6379:6379 redis
