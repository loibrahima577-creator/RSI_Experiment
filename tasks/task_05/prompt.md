# Task 05: chunk_list

Implement `chunk_list(items, size)`. Return a list of consecutive slices of `items`, each of length `size` except possibly the last. Raise `ValueError` if `size` is not a positive integer. Do not mutate the input.

Examples:
- `chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]`
- `chunk_list([], 3) == []`
