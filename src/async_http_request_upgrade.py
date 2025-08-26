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
from aiohttp import ClientResponseError, ClientTimeout


# Вспомогательная генерация списка URL для тестов
def generate_test_urls(filename="urls.txt", count=10):
    base_url = "https://jsonplaceholder.typicode.com/todos/"
    with open(filename, "w", encoding="utf-8") as f:
        for i in range(1, count + 1):
            f.write(f"{base_url}{i}\n")


# Основная оркестрация: очередь и распределение заданий
async def fetch_urls(input_file: str, output_file: str, concurrency: int = 5):
    queue = asyncio.Queue(maxsize=concurrency * 2)

    # Очистить выходной файл заранее
    async with aiofiles.open(output_file, "w", encoding="utf-8") as f:
        await f.write("")

    timeout = ClientTimeout(total=None, sock_connect=30, sock_read=600)
    async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
        tasks = [
            asyncio.create_task(worker(f"worker-{i + 1}", queue, session, output_file))
            for i in range(concurrency)
        ]
        async for url in read_urls(input_file):
            await queue.put(url)
        for _ in range(concurrency):
            await queue.put(None)
        await asyncio.gather(*tasks)


# Асинхронный генератор для чтения URL из файла
async def read_urls(file_path: str):
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        async for line in f:
            url = line.strip()
            if url:
                yield url


# Асинхронная запись результата
async def write_result(output_file: str, url: str, data):
    line = json.dumps({url: data}, ensure_ascii=False)
    async with aiofiles.open(output_file, "a", encoding="utf-8") as f:
        await f.write(line + "\n")


# Асинхронный парсинг JSON через executor для избежания блокировки event loop
async def parse_json_bytes(body_bytes: bytes):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, json.loads, body_bytes.decode("utf-8"))


# Только запрос и raise_if_status; парсинг — отдельной функцией
async def fetch(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as resp:
        resp.raise_for_status()
        body = await resp.read()
        return await parse_json_bytes(body)


# Воркеры забирают задания из очереди, централизованно логируют и обрабатывают исключения
async def worker(name, queue, session, output_file):
    while True:
        url = await queue.get()
        if url is None:
            queue.task_done()
            break
        try:
            data = await fetch(session, url)
        except ClientResponseError as e:
            print(f"{name}: HTTP {e.status} for {url}")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"{name}: Network error for {url}: {e}")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"{name}: JSON decode error for {url}: {e}")
        else:
            await write_result(output_file, url, data)
        finally:
            queue.task_done()


if __name__ == "__main__":
    input_file = "urls.txt"
    output_file = "result.jsonl"

    generate_test_urls(input_file, count=10)
    asyncio.run(fetch_urls(input_file, output_file))
