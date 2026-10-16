from solution import intersection_labels

assert intersection_labels(["oak", "ash"], ["ash", "elm"]) == ("ash",)
assert intersection_labels(["Red", "blue"], ["BLUE", "red"]) == ("Red", "blue")
assert intersection_labels(["a", "b", "c"], ["c", "a"]) == ("a", "c")
assert intersection_labels([], ["x"]) is None
left = ["a", "b"]
right = ["B", "a"]
intersection_labels(left, right)
assert left == ["a", "b"] and right == ["B", "a"]
