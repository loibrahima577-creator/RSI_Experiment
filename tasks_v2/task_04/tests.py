from solution import most_common_word

assert most_common_word(["Tea", "tea", "TEA", "soup"]) == "Tea"
assert most_common_word(["plum", "pear", "plum"]) == "plum"
assert most_common_word(["x"]) == "x"
assert most_common_word(["left", "right"]) == "left"
assert most_common_word([]) is None
