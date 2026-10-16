from solution import sort_labels

assert sort_labels(["pear", "apple"]) == ("apple", "pear")
assert sort_labels(["beta", "ALPHA", "gamma"]) == ("ALPHA", "beta", "gamma")
assert sort_labels(["Oak", "oak", "PINE"]) == ("Oak", "PINE")
source = ["pear", "Apple", "PEAR"]
sort_labels(source)
assert source == ["pear", "Apple", "PEAR"]
try:
    sort_labels(["ok", None])
except ValueError:
    pass
else:
    assert False, "non-string labels must fail"
