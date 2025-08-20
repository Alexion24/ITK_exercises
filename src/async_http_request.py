# Напишите асинхронную функцию fetch_urls, которая принимает список URL-адресов и возвращает словарь,
# где ключами являются URL, а значениями — статус-коды ответов. Используйте библиотеку aiohttp для выполнения HTTP-запросов.
#
# Требования:
# Ограничьте количество одновременных запросов до 5 (используйте примитивы синхронизации из asyncio библиотеки)
# Обработайте возможные исключения (например, таймауты, недоступные ресурсы) и присвойте соответствующие статус-коды
# (например, 0 для ошибок соединения).
# Сохраните все результаты в файл

import asyncio
import json

import aiohttp
from aiohttp import ClientError

URLS = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
]


async def fetch_url(session: aiohttp.ClientSession, url: str, sem: asyncio.Semaphore) -> tuple[str, int]:
    """Выполнение одного запроса с обработкой ошибок."""
    async with sem:  # ограничиваем число одновременных запросов
        try:
            async with session.get(url, timeout=10) as response:
                return url, response.status
        except (asyncio.TimeoutError, ClientError, Exception):
            # Возвращаем 0 для любых ошибок сети
            return url, 0
        

async def fetch_urls(urls: list[str], file_path: str):
    results = {}
    sem = asyncio.Semaphore(5)  # максимум 5 параллельных запросов

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url, sem) for url in urls]
        for cor in asyncio.as_completed(tasks):  # собираем результаты по мере готовности
            url, status = await cor
            results[url] = status

    with open(file_path, "w", encoding="utf-8") as f:
        for url, status in results.items():
            json.dump({url: status}, f, ensure_ascii=False)
            f.write("\n")

    return results


if __name__ == "__main__":
    asyncio.run(fetch_urls(URLS, "./results.jsonl"))
