from solution import topological_order

assert topological_order(["a", "b", "c"], [("a", "b"), ("b", "c")]) == ("a", "b", "c")
assert topological_order(["a", "b", "c"], []) == ("a", "b", "c")
assert topological_order(["x", "y", "z"], [("x", "z")]) == ("x", "y", "z")
nodes = ["a", "b", "c"]
edges = [("a", "b")]
topological_order(nodes, edges)
assert nodes == ["a", "b", "c"] and edges == [("a", "b")]
try:
    topological_order(["a", "b"], [("a", "b"), ("b", "a")])
except ValueError:
    pass
else:
    assert False, "cycles must fail"
