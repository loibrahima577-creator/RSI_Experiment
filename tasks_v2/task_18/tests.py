from solution import shortest_path

assert shortest_path({"a": ["b", "c"], "b": ["a", "c"], "c": ["a", "b"]}, "a", "c") == ("a", "c")
assert shortest_path({"a": ["b"], "b": ["a", "c"], "c": ["b"]}, "a", "c") == ("a", "b", "c")
assert shortest_path({"a": []}, "a", "a") == ("a",)
assert shortest_path({"a": [], "b": []}, "a", "b") is None
assert shortest_path({}, "a", "b") is None
graph = {"a": ["b"], "b": ["a"]}
shortest_path(graph, "a", "b")
assert graph == {"a": ["b"], "b": ["a"]}
try:
    shortest_path({"a": []}, "a", "missing")
except ValueError:
    pass
else:
    assert False, "unknown nodes must fail"
