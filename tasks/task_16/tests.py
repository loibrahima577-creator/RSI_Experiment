from solution import merge_intervals

assert merge_intervals([[1, 3], [2, 5], [8, 9]]) == [[1, 5], [8, 9]]
assert merge_intervals([[1, 2], [2, 4]]) == [[1, 4]]
assert merge_intervals([]) == []
assert merge_intervals([[5, 6], [1, 2], [3, 4]]) == [[1, 2], [3, 4], [5, 6]]
assert merge_intervals([[1, 10], [2, 3], [4, 5]]) == [[1, 10]]
source = [[2, 4], [1, 3]]
assert merge_intervals(source) == [[1, 4]]
assert source == [[2, 4], [1, 3]]
