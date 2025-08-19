# Дан отсортированный по возрастанию список чисел, который может содержать миллионы элементов.
# Необходимо написать функцию search(number: int, numbers: list) -> bool,
# которая принимает число number и возвращает True, если это число находится в списке numbers.
# Требуемая временная сложность алгоритма — O(log n).


numbers = [1, 2, 3, 45, 356, 569, 600, 705, 923]


def search(number: int) -> bool:
    left, right = 0, len(numbers) - 1
    while left <= right:
        mid = (left + right) // 2
        if numbers[mid] == number:
            return True
        elif numbers[mid] < number:
            left = mid + 1
        else:
            right = mid - 1
    return False


print(search(66))
