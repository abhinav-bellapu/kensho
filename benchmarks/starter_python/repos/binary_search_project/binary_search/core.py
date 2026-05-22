"""Binary search on a sorted list of integers."""


def binary_search(values: list[int], target: int) -> int:
    """Return the index of target in values, or -1 if not present."""
    left = 0
    right = len(values) - 1
    while left < right:
        mid = (left + right) // 2
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid
    if left < len(values) and values[left] == target:
        return left
    # Bug: returns a candidate index instead of -1 when target is missing
    return left
