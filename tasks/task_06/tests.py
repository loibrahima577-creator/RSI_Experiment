from solution import common_prefix

assert common_prefix(["flower", "flow", "flight"]) == "fl"
assert common_prefix(["dog", "cat"]) == ""
assert common_prefix([]) == ""
assert common_prefix(["same", "same"]) == "same"
assert common_prefix(["", "abc"]) == ""
assert common_prefix(["Case", "case"]) == ""
