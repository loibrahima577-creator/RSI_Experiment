from solution import chunk_list

assert chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
assert chunk_list([], 3) == []
assert chunk_list([1, 2], 5) == [[1, 2]]
assert chunk_list([1, 2, 3], 1) == [[1], [2], [3]]
try:
    chunk_list([1], 0)
except ValueError:
    pass
else:
    assert False, "size must be positive"
