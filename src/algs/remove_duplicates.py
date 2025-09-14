NUMS = [1, 1, 2, 2, 3, 4, 4, 5]


def remove_duplicates(nums: list[int]) -> tuple[int, list[int]]:
    if not nums:
        return 0, []

    # указатель на последний уникальный элемент
    last_idx = 0
    for new_idx in range(1, len(nums)):
        if nums[new_idx] != nums[last_idx]:
            last_idx += 1
            nums[last_idx] = nums[new_idx]
    # Длина уникальных элементов - last_idx + 1
    return last_idx + 1, nums[: last_idx + 1]


if __name__ == "__main__":
    k, output = remove_duplicates(NUMS)
    print(k, output)
