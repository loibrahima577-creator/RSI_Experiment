from solution import matrix_multiply

assert matrix_multiply([[1, 2]], [[3], [4]]) == ((11,),)
assert matrix_multiply([[2]], [[5]]) == ((10,),)
assert matrix_multiply([[1, 0], [0, 1]], [[7, 8], [9, 10]]) == ((7, 8), (9, 10))
assert matrix_multiply([[1, 2, 3]], [[1], [1], [1]]) == ((6,),)
left = [[1, 2], [3, 4]]
right = [[5], [6]]
matrix_multiply(left, right)
assert left == [[1, 2], [3, 4]] and right == [[5], [6]]
try:
    matrix_multiply([[1, 2]], [[1, 2]])
except ValueError:
    pass
else:
    assert False, "incompatible dimensions must fail"
