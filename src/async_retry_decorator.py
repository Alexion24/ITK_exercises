import asyncio
import logging
from functools import wraps

# Настройка логирования для более информативного вывода
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S"
)


def async_retry(retries: int, exceptions: tuple, delay: float = 1.0):
    """
    Фабрика декораторов для повторного выполнения асинхронной функции.

    Эта функция создает и возвращает декоратор, который будет повторять
    выполнение обернутой асинхронной функции в случае возникновения
    одного из указанных исключений.

    Args:
        retries (int): Максимальное количество повторных попыток.
        exceptions (tuple): Кортеж с классами исключений, при которых
                            следует выполнять повтор.
        delay (float): Задержка в секундах между попытками.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            # Цикл выполнится `retries + 1` раз: первая попытка + `retries` повторов.
            for attempt in range(retries + 1):
                try:
                    # Выполняем асинхронную функцию
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    # Проверяем, остались ли еще попытки
                    if attempt < retries:
                        logging.warning(
                            f"Retrying {func.__name__} (attempt {attempt + 1}/{retries})... "
                            f"Error: {e}"
                        )
                        # Асинхронная пауза перед следующей попыткой
                        await asyncio.sleep(delay)
                    else:
                        logging.error(f"All retries for {func.__name__} failed.")
                        # Если попытки исчерпаны, пробрасываем последнее исключение
                        raise last_exception

        return wrapper

    return decorator


@async_retry(retries=3, exceptions=(ValueError,), delay=0.5)
async def unstable_task():
    """Эта задача всегда падает с ошибкой ValueError."""
    logging.info("Running task...")
    raise ValueError("Something went wrong")


async def main():
    try:
        await unstable_task()
    except Exception as e:
        # Это исключение будет поймано после того, как все попытки будут исчерпаны
        logging.error(f"Final failure after all retries: {e}")


# Запуск асинхронного приложения
if __name__ == "__main__":
    asyncio.run(main())
