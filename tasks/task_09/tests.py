from solution import sort_by_frequency

assert sort_by_frequency(["pear", "fig", "pear", "plum", "fig"]) == ["fig", "pear", "plum"]
assert sort_by_frequency(["b", "a"]) == ["a", "b"]
assert sort_by_frequency([]) == []
assert sort_by_frequency(["x", "x", "x"]) == ["x"]
assert sort_by_frequency(["A", "a", "A"]) == ["A", "a"]
assert sort_by_frequency(["z", "y", "z", "y", "x"]) == ["y", "z", "x"]
