# Задача - Очередь
# Реализуйте класс очереди который использует редис под капотом


import json

import redis


class RedisQueue:
    def __init__(
        self, name="queue", redis_host="localhost", redis_port=6379, redis_db=0
    ):
        self._redis = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db, decode_responses=True
        )
        self._name = name

    def publish(self, msg: dict):
        # Сериализуем словарь в JSON и добавляем в конец списка
        msg_json = json.dumps(msg)
        self._redis.rpush(self._name, msg_json)

    def consume(self) -> dict | None:
        # Извлекаем JSON из начала списка и десериализуем в словарь
        msg_json = self._redis.lpop(self._name)
        if msg_json is None:
            return None
        return json.loads(msg_json)


if __name__ == "__main__":
    q = RedisQueue()
    q.publish({"a": 1})
    q.publish({"b": 2})
    q.publish({"c": 3})

    assert q.consume() == {"a": 1}
    assert q.consume() == {"b": 2}
    assert q.consume() == {"c": 3}
