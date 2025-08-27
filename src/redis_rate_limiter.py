# Ваше приложение делает HTTP запросы в сторонний сервис (функция make_api_request),
# при этом сторонний сервис имеет проблемы с производительностью и ваша задача ограничить
# количество запросов к этому сервису - не больше пяти запросов за последние три секунды.
# Ваша задача реализовать RateLimiter.test метод который:
#
# 1) возвращает True в случае если лимит на кол-во запросов не достигнут
# 2) возвращает False если за последние 3 секунды уже сделано 5 запросов.
# Ваша реализация должна использовать Redis, т.к. предполагается что приложение работает на нескольких серверах.


import random
import time

import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(self, redis_client=None, key="rate_limiter", limit=5, period=3):
        if redis_client is None:
            # По-умолчанию подключаемся к localhost
            self.redis = redis.Redis(host="localhost", port=6379, db=0)
        else:
            self.redis = redis_client
        self.key = key
        self.limit = limit
        self.period = period

    def test(self) -> bool:
        now = time.time()
        pipe = self.redis.pipeline()

        # Очищаем метки старше окна лимита
        min_time = now - self.period
        # Используем Sorted Set для хранения таймштампов запросов
        pipe.zremrangebyscore(self.key, 0, min_time)
        # Добавляем текущий запрос
        pipe.zadd(self.key, {str(now): now})
        # Получаем количество запросов за окно
        pipe.zcard(self.key)
        # Автоматически чистим ключ через period + 1
        pipe.expire(self.key, self.period + 1)
        _, _, count, _ = pipe.execute()

        return count <= self.limit


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == "__main__":
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(random.randint(1, 2))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
