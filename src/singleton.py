# Реализуйте паттерн синглтон тремя способами:
# с помощью метаклассов
# с помощью метода __new__ класса
# через механизм импортов


# --- 1. Синглтон через метакласс ---
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonMetaClass(metaclass=SingletonMeta):
    def __init__(self, value):
        self.value = value


# --- 2. Синглтон через __new__ ---
class SingletonNew:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, value):
        if not hasattr(self, "value"):  # чтобы не перезаписывать при повторных вызовах
            self.value = value


# --- 3. Синглтон через импорт ---
# В реальной ситуации это отдельный модуль.
# Здесь просто эмулируем через глобальный объект.
class Config:
    def __init__(self, value):
        self.value = value


singleton_import = Config("import-style singleton")


# --- Проверки ---
if __name__ == "__main__":
    print("=== 1. Метакласс ===")
    a1 = SingletonMetaClass("first")
    b1 = SingletonMetaClass("second")
    print(a1.value, b1.value)
    print("Одинаковый объект:", a1 is b1)

    print("\n=== 2. __new__ ===")
    a2 = SingletonNew("first")
    b2 = SingletonNew("second")
    print(a2.value, b2.value)
    print("Одинаковый объект:", a2 is b2)

    print("\n=== 3. Импорты (эмуляция) ===")
    a3 = singleton_import
    b3 = singleton_import
    print(a3.value, b3.value)
    print("Одинаковый объект:", a3 is b3)
