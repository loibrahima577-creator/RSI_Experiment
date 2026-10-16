from solution import transpose_matrix

assert transpose_matrix([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
assert transpose_matrix([[1], [2]]) == [[1, 2]]
assert transpose_matrix([]) == []
assert transpose_matrix([[], []]) == []
source = [[1, 2], [3, 4]]
assert transpose_matrix(source) == [[1, 3], [2, 4]]
assert source == [[1, 2], [3, 4]]
try:
    transpose_matrix([[1], [2, 3]])
except ValueError:
    pass
else:
    assert False, "ragged matrix must fail"
