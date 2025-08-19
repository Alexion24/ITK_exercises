import datetime


class CreatedAtMeta(type):
    def __new__(mcs, name, bases, namespace):
        # Добавляем атрибут created_at в класс при его создании
        namespace["created_at"] = datetime.datetime.now()
        return super().__new__(mcs, name, bases, namespace)


# Пример использования:
class MyClass(metaclass=CreatedAtMeta):
    pass


class AnotherClass(metaclass=CreatedAtMeta):
    pass


print(MyClass.created_at)  # Время создания класса MyClass
print(AnotherClass.created_at)  # Время создания класса AnotherClass
