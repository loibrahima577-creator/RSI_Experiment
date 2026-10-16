from solution import shortest_path

assert shortest_path([[0, 0], [1, 0]], (0, 0), (1, 1)) == [(0, 0), (0, 1), (1, 1)]
assert shortest_path([[0, 1]], (0, 0), (0, 1)) == []
assert shortest_path([[0]], (0, 0), (0, 0)) == [(0, 0)]
assert shortest_path([[1]], (0, 0), (0, 0)) == []
assert shortest_path([[0, 0, 0]], (0, 0), (0, 2)) == [(0, 0), (0, 1), (0, 2)]
assert shortest_path([[0, 1], [1, 0]], (0, 0), (1, 1)) == []
assert shortest_path([[0, 0]], (0, 0), (2, 0)) == []
