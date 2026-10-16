from solution import group_words

assert group_words(["apple", "berry", "apricot"]) == (("a", ("apple", "apricot")), ("b", ("berry",)))
assert group_words(["Oak", "olive", "Pine"]) == (("o", ("Oak", "olive")), ("p", ("Pine",)))
assert group_words(["one", "two", "three"]) == (("o", ("one",)), ("t", ("two", "three")))
assert group_words([]) is None
source = ["apple", "berry"]
group_words(source)
assert source == ["apple", "berry"]
