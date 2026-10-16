from solution import normalize_whitespace

assert normalize_whitespace("  red\tblue  ") == "red blue"
assert normalize_whitespace("a\n\n b") == "a b"
assert normalize_whitespace("") == ""
assert normalize_whitespace(" \t\n") == ""
assert normalize_whitespace("one") == "one"
