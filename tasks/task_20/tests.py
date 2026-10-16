from solution import connected_components

assert connected_components(5, [(0, 1), (1, 2), (3, 4)]) == [[0, 1, 2], [3, 4]]
assert connected_components(3, []) == [[0], [1], [2]]
assert connected_components(0, []) == []
assert connected_components(4, [(2, 1), (1, 2)]) == [[0], [1, 2], [3]]
assert connected_components(4, [(0, 3), (1, 2), (2, 3)]) == [[0, 1, 2, 3]]
assert connected_components(2, [(0, 0)]) == [[0], [1]]
