from solution import rotate_list

assert rotate_list([1, 2, 3, 4], 1) == [4, 1, 2, 3]
assert rotate_list([1, 2, 3], -1) == [2, 3, 1]
assert rotate_list([1, 2, 3], 3) == [1, 2, 3]
assert rotate_list([], 5) == []
source = [1, 2, 3]
assert rotate_list(source, 1) == [3, 1, 2]
assert source == [1, 2, 3]
