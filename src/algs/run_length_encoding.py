def run_length_encoding_iterative(s: str) -> str:
    if not s:
        return ""

    encoded_parts = []
    count = 1
    # Начинаем со второго символа, сравнивая его с предыдущим
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            # Записываем результат для предыдущей последовательности
            encoded_parts.append(s[i - 1] + str(count))
            # Сбрасываем счетчик для новой последовательности
            count = 1

    # Добавляем последнюю последовательность символов после завершения цикла
    encoded_parts.append(s[-1] + str(count))

    return "".join(encoded_parts)


if __name__ == "__main__":
    s = "AAABBCCDDD"
    print(run_length_encoding_iterative(s))
