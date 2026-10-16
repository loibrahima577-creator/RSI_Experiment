from solution import normalize_tags

assert normalize_tags(["red", "blue"]) == ("red", "blue")
assert normalize_tags(["oak", "OAK", "pine"]) == ("oak", "pine")
assert normalize_tags(["x", "X", "x"]) == ("x",)
source = ["red", "RED", "green"]
normalize_tags(source)
assert source == ["red", "RED", "green"]
assert normalize_tags([]) is None
