from solution import interleave

assert interleave([1, 2], ["a", "b"]) == (1, "a", 2, "b")
assert interleave([7], [8]) == (7, 8)
assert interleave([], []) is None
left = [1, 2]
right = [3, 4]
interleave(left, right)
assert left == [1, 2] and right == [3, 4]
try:
    interleave([1], [2, 3])
except ValueError:
    pass
else:
    assert False, "different lengths must fail"
