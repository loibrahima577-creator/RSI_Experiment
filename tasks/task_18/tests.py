from solution import spiral_order

assert spiral_order([[1, 2, 3], [4, 5, 6]]) == [1, 2, 3, 6, 5, 4]
assert spiral_order([[1], [2], [3]]) == [1, 2, 3]
assert spiral_order([]) == []
assert spiral_order([[], []]) == []
assert spiral_order([[1, 2], [3, 4]]) == [1, 2, 4, 3]
assert spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]
