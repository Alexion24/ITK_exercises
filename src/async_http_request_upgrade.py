# Напишите асинхронную функцию fetch_urls, которая принимает файл со списком урлов
# (каждый URL адрес возвращает JSON) и сохраняет результаты выполнения в другой файл (result.jsonl),
# где ключами являются URL, а значениями — распарсенный json, при условии что статус код — 200.
# Используйте библиотеку aiohttp для выполнения HTTP-запросов.
#
# Требования:
# Ограничьте количество одновременных запросов до 5
# Обработайте возможные исключения (например, таймауты, недоступные ресурсы) ошибок соединения

# Контекст:
# Урлов в файле может быть десятки тысяч
# Некоторые урлы могут весить до 300-500 мегабайт
# При внезапной остановке и/или перезапуске скрипта - допустимо скачивание урлов по новой.


import asyncio
import json

import aiofiles
import aiohttp
from aiohttp import ClientTimeout


async def fetch_url(
    session: aiohttp.ClientSession, url: str, sem: asyncio.Semaphore, output_file: str
):
    """
    Загружает JSON по url и сохраняет результат в файл output_file в формате JSONL.
    Каждая строка файла: { "<url>": <parsed_json> }
    """
    async with sem:  # ограничиваем кол-во одновременных запросов
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json(
                        content_type=None
                    )  # не доверяем заголовку content-type
                    line = json.dumps({url: data}, ensure_ascii=False)
                    # безопасная асинхронная запись в файл
                    async with aiofiles.open(output_file, "a", encoding="utf-8") as f:
                        await f.write(line + "\n")
                else:
                    print(f"⚠️ Пропущено {url}, статус: {response.status}")
        except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError) as e:
            print(f"❌ Ошибка при обработке {url}: {e}")


async def fetch_urls(
    input_file: str = "urls.txt",
    output_file: str = "result.jsonl",
    concurrency: int = 5,
):
    """
    Читает url из input_file, асинхронно скачивает данные
    и сохраняет результат в output_file в JSONL.
    """
    # читаем url
    async with aiofiles.open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in await f.readlines() if line.strip()]

    # очищаем выходной файл перед записью
    async with aiofiles.open(output_file, "w", encoding="utf-8") as f:
        await f.write("")

    timeout = ClientTimeout(
        total=None, sock_connect=30, sock_read=600
    )  # гибкий timeout
    sem = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
        tasks = [fetch_url(session, url, sem, output_file) for url in urls]
        # используем asyncio.as_completed для "стриминга" результатов
        for task in asyncio.as_completed(tasks):
            await task


def generate_test_urls(filename="urls.txt", count=10):
    base_url = "https://jsonplaceholder.typicode.com/todos/"
    with open(filename, "w", encoding="utf-8") as f:
        for i in range(1, count + 1):
            url = f"{base_url}{i}"
            f.write(url + "\n")


if __name__ == "__main__":
    input_file = "urls.txt"
    output_file = "result.jsonl"

    # Генерация тестового файла с url
    generate_test_urls(input_file, count=10)

    # Запуск основного асинхронного процесса
    asyncio.run(fetch_urls(input_file, output_file))
