from solution import count_islands

assert count_islands([[1, 0], [0, 1]]) == 2
assert count_islands([[1, 1], [0, 1]]) == 1
assert count_islands([[0, 0], [0, 0]]) == 0
assert count_islands([]) is None
grid = [[1, 0], [0, 1]]
count_islands(grid)
assert grid == [[1, 0], [0, 1]]
try:
    count_islands([[1, 0], [1]])
except ValueError:
    pass
else:
    assert False, "ragged grids must fail"
