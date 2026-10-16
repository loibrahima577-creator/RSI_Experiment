from solution import flatten_once

assert flatten_once([[1, 2], 3, (4, 5)]) == [1, 2, 3, 4, 5]
assert flatten_once([[1, [2]]]) == [1, [2]]
assert flatten_once([]) == []
assert flatten_once(["ab", ["c"]]) == ["ab", "c"]
assert flatten_once([(1,), (), 2]) == [1, 2]
