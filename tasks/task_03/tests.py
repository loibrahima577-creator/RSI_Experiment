from solution import unique_preserve_order

assert unique_preserve_order([3, 1, 3, 2, 1]) == [3, 1, 2]
assert unique_preserve_order([]) == []
assert unique_preserve_order(["a", "a", "b"]) == ["a", "b"]
assert unique_preserve_order([1, "1", 1]) == [1, "1"]
source = [2, 2, 4]
assert unique_preserve_order(source) == [2, 4]
assert source == [2, 2, 4]
