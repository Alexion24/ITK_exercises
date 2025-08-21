import csv
import json
import math
import random
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, Process, Queue, cpu_count


# ---------- Сбор данных ----------
def generate_data(n: int) -> list[int]:
    return [random.randint(1, 1000) for _ in range(n)]


# ---------- Обработка ----------
def is_prime(number: int) -> bool:
    if number < 2:
        return False
    if number % 2 == 0:
        return number == 2
    sqrt_n = int(math.sqrt(number)) + 1
    for i in range(3, sqrt_n, 2):
        if number % i == 0:
            return False
    return True


def process_number(number: int) -> dict:
    # Возвращаем словарь для сохранения
    return {"number": number, "is_prime": is_prime(number)}


# ---------- Варианты обработки ----------


# Однопроцессный (без параллелизации)
def single_threaded(data):
    return [process_number(num) for num in data]


# Вариант А: ThreadPoolExecutor
def thread_pool(data):
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        return list(executor.map(process_number, data))


# Вариант Б: multiprocessing.Pool
def process_pool(data):
    with Pool(processes=cpu_count()) as pool:
        return pool.map(process_number, data)


# Вариант В: multiprocessing.Process + Queue
def worker(input_q: Queue, output_q: Queue):
    while True:
        num = input_q.get()
        if num is None:
            break
        output_q.put(process_number(num))


def process_with_queues(data):
    input_q = Queue()
    output_q = Queue()

    # Создаём процессы
    processes = [
        Process(target=worker, args=(input_q, output_q)) for _ in range(cpu_count())
    ]

    for p in processes:
        p.start()

    # Кладём данные
    for num in data:
        input_q.put(num)

    # Посылаем сигналы на завершение
    for _ in processes:
        input_q.put(None)

    results = []
    for _ in range(len(data)):
        results.append(output_q.get())

    for p in processes:
        p.join()

    return results


# ---------- Сохранение ----------
def save_results_json(results, filename="results.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def save_results_csv(results, filename="results.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["number", "is_prime"])
        writer.writeheader()
        writer.writerows(results)


# ---------- Сравнение ----------
def benchmark(func, data, name):
    start = time.perf_counter()
    results = func(data)
    elapsed = time.perf_counter() - start
    return name, elapsed, results


if __name__ == "__main__":
    N = 100_000  # можно увеличить, чтобы эффект был заметнее
    data = generate_data(N)

    benchmarks = []
    for func, name in [
        (single_threaded, "Single-threaded"),
        (thread_pool, "ThreadPoolExecutor"),
        (process_pool, "Multiprocessing.Pool"),
        (process_with_queues, "Multiprocessing.Process+Queue"),
    ]:
        print(f"Running {name}...")
        name, elapsed, results = benchmark(func, data, name)
        benchmarks.append((name, elapsed))
        # Сохраняем только для последнего варианта
        if name == "Multiprocessing.Process+Queue":
            save_results_json(results)
            save_results_csv(results)

    print("\n=== Benchmark Results ===")
    print("{:<35} {:>10}".format("Method", "Time, s"))
    print("-" * 50)
    for name, elapsed in benchmarks:
        print("{:<35} {:>10.3f}".format(name, elapsed))
