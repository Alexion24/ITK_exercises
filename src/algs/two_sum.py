NUMS = [2, 7, 11, 15]
TARGET = 9


def find_two_sum(nums: list, target: int) -> list:
    num_to_index = {}
    for idx, num in enumerate(nums):
        if target - num in num_to_index:
            return [num_to_index[target - num], idx]
        num_to_index[num] = idx
    return []


if __name__ == "__main__":
    print(find_two_sum(NUMS, TARGET))
