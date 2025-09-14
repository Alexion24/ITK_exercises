def longest_incr_subseq(nums: list[int]) -> int:
    """
    Находит длину наибольшей НЕПРЕРЫВНОЙ возрастающей подпоследовательности.
    """
    if not nums:
        return 0

    max_len = 1
    current_len = 1

    for i in range(1, len(nums)):
        if nums[i] > nums[i - 1]:
            # Последовательность продолжается
            current_len += 1
        else:
            # Последовательность прервалась, начинаем новую
            current_len = 1

        # Обновляем максимальную найденную длину
        max_len = max(max_len, current_len)

    return max_len


if __name__ == "__main__":
    nums = [10, 9, 2, 5, 3, 7, 101, 18]
    print(f"Input: {nums}")
    print(
        f"Максимальная длина непрерывной возрастающей последовательности: {longest_incr_subseq(nums)}"
    )
    # Ожидаемый вывод: 3
